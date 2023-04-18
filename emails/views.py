import json
import base64

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)

from rest_framework_api_key.permissions import HasAPIKey

from knox.auth import TokenAuthentication


from proeliumx.utils import BAD_REQUEST_RESPONSE
from emails.tasks import send_email_task
from emails.s3 import create_presigned_s3_post
from emails.models import Email, ChartPNG
from emails.utils import get_cdn_url


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes(
    [
        IsAuthenticated,
        #   HasAPIKey
    ]
)
def get_presigned_post_view(request):
    params = request.data.get("params", None)
    size = request.data.get("size", None)
    if None in [params, size] or size > 1 * 1024 * 1024:  # 1 MB
        return BAD_REQUEST_RESPONSE

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
@permission_classes([IsAuthenticated, HasAPIKey])
def post_email_view(request):
    to = request.data.get("to", None)
    subject = request.data.get("subject", None)
    html_message = request.data.get("html_message", None)
    chart_pngs_ids = request.data.get("chart_pngs", None)
    type = request.data.get("type", None)

    if None in [html_message, to, subject, chart_pngs_ids, type]:
        return BAD_REQUEST_RESPONSE

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
        sender=request.user.username + "@creators.proeliumx.com",
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
    pass
