import json
import base64
from svix.webhooks import Webhook, WebhookVerificationError


from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)


from knox.auth import TokenAuthentication


from getabranddeal.utils import BAD_REQUEST_RESPONSE, get_serializer_first_error
from emails.tasks import send_email_task
from emails.s3 import create_presigned_s3_post
from emails.models import Email, ChartPNG
from emails.utils import get_cdn_url
from emails.serializers import (
    EmailValidSerializer,
    SettingsSerializer,
    EmailShortSerializer,
    EmailLongSerializer,
)


CREATOR_MAIL_DOMAIN = settings.CREATOR_MAIL_DOMAIN
RESEND_WEBHOOK_SIGNING_KEY = settings.RESEND_WEBHOOK_SIGNING_KEY
RESEND_TYPE = {
    "email.sent": Email.SENT,
    "email.delivered": Email.DELIVERED,
    "email.delivery_delayed": Email.DELIVERY_DELAYED,
    "email.complained": Email.COMPLAINED,
    "email.bounced": Email.BOUNCED,
    "email.open": Email.OPENED,
    "email.clicked": Email.CLICKED,
}

GET_EMAILS_COUNT = 20


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_settings_view(request):
    settings = request.user.settings
    settings_data = SettingsSerializer(settings).data
    return JsonResponse(
        {
            "detail": "Settings retrieved successfully",
            "payload": {"settings": settings_data},
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_emails_view(request):
    page = request.data.get("page", 0)
    emails = Email.objects.filter(user=request.user).order_by("-created_at")[
        (page * GET_EMAILS_COUNT) : ((page + 1) * GET_EMAILS_COUNT)
    ]
    emails_data = EmailShortSerializer(emails, many=True).data
    return JsonResponse(
        {
            "detail": "Emails retrieved successfully",
            "payload": {"emails": emails_data},
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_email_view(request):
    email_id = request.data.get("email_id", None)
    if email_id is None:
        return BAD_REQUEST_RESPONSE
    try:
        email = Email.objects.get(id=email_id, user=request.user)
    except Email.DoesNotExist:
        return BAD_REQUEST_RESPONSE
    email_data = EmailLongSerializer(email).data
    return JsonResponse(
        {
            "detail": "Email retrieved successfully",
            "payload": {"email": email_data},
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_presigned_post_view(request):
    params = request.data.get("params", None)
    size = request.data.get("size", None)
    if None in [params, size] or size > 2 * 1024 * 1024:  # 2 MB
        return BAD_REQUEST_RESPONSE

    params = dict(sorted(params.items()))
    json_str = json.dumps(params)
    filename = base64.b64encode(json_str.encode("utf-8")).decode("utf-8") + ".png"
    file_path = request.user.username + "/" + filename
    try:
        chart_png = ChartPNG.objects.get(user=request.user, path=file_path)
        return JsonResponse(
            {
                "detail": "ChartPNG already exists",
                "payload": {
                    "chart_png_id": chart_png.id,
                    "chart_png_url": get_cdn_url(chart_png.path),
                },
            },
            status=status.HTTP_208_ALREADY_REPORTED,
        )
    except ChartPNG.DoesNotExist:
        presigned_post = create_presigned_s3_post(size, file_path)
        if presigned_post is None:
            return BAD_REQUEST_RESPONSE
        chart_png = ChartPNG.objects.create(
            user=request.user, path=file_path, params=params
        )

        return JsonResponse(
            {
                "detail": "Presigned post",
                "payload": {
                    "url": presigned_post,
                    "chart_png_id": chart_png.id,
                    "chart_png_url": get_cdn_url(chart_png.path),
                },
            },
            status=status.HTTP_200_OK,
        )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def post_email_view(request):
    # TODO only 100 emails per day
    to = request.data.get("to", None)
    subject = request.data.get("subject", None)
    html_message = request.data.get("html_message", None)
    plain_message = request.data.get("plain_message", None)
    chart_pngs_ids = request.data.get("chart_pngs", None)
    type = request.data.get("type", None)

    if type == Email.TEST:
        to = request.user.email

    serializer = EmailValidSerializer(
        data={
            "user": request.user.id,
            "to": to,
            "subject": subject,
            "html_message": html_message,
            "plain_message": plain_message,
            "sender": request.user.username + f"@{CREATOR_MAIL_DOMAIN}",
            "reply_to": request.user.email,
            "type": type,
        }
    )

    if not serializer.is_valid():
        return JsonResponse(
            {
                "detail": get_serializer_first_error(serializer.errors),
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    # TODO Use serializer.save() instead of creating email manually
    if Email.objects.filter(
        to=to, created_at__gt=timezone.now() - timezone.timedelta(days=7)
    ).exists():
        return JsonResponse(
            {"detail": "Emails to a brand can only be sent once a week"},
            status=status.HTTP_403_FORBIDDEN,
        )

    email = Email.objects.create(
        user=request.user,
        to=to,
        subject=subject,
        html_message=html_message,
        plain_message=plain_message,
        sender=request.user.username + f"@{CREATOR_MAIL_DOMAIN}",
        reply_to=request.user.email,
        type=type,
    )

    # Add email to chart_pngs
    for chart_png in ChartPNG.objects.filter(id__in=chart_pngs_ids):
        chart_png.emails.add(email)

    send_email_task.delay(email.id)
    return JsonResponse({"detail": "Email queued"}, status=status.HTTP_200_OK)


@csrf_exempt
def resend_webhook_view(request):
    headers = request.headers
    payload = request.body
    try:
        wh = Webhook(RESEND_WEBHOOK_SIGNING_KEY)
        data = wh.verify(payload, headers)
        try:
            email = Email.objects.get(message_id=data["data"]["email_id"])
            email.status = RESEND_TYPE[data["type"]]
            email.save(update_fields=["status"])
        except (Exception, Email.DoesNotExist) as e:
            print("ERROR", e)
        return HttpResponse(status=200)
    except WebhookVerificationError as e:
        return HttpResponse(status=400)
