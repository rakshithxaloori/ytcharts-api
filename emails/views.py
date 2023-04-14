import json
import base64
from django.http import JsonResponse

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

# TODO SES Notifications success, failed view


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def get_presigned_post_view(request):
    params = request.data.get("params", None)
    size = request.data.get("size", None)
    if params is None or size > 5 * 1024 * 1024:  # 5 MB
        return BAD_REQUEST_RESPONSE

    json_str = json.dumps(params)
    filename = base64.b64encode(json_str.encode("utf-8")).decode("utf-8") + ".png"
    file_path = request.user.username + "/" + filename

    presigned_post = create_presigned_s3_post(size, file_path)
    if presigned_post is None:
        return BAD_REQUEST_RESPONSE
    chart_png = ChartPNG.objects.create(user=request.user, path=file_path)
    presigned_post["chart_png_id"] = chart_png.id
    return JsonResponse(
        {"detail": "Presigned post", "payload": {"url": presigned_post}},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def post_email_view(request):
    html_message = request.data.get("html_message", None)
    brand_email = request.data.get("brand_email", None)
    subject = request.data.get("subject", None)

    if None in [html_message, brand_email, subject]:
        return BAD_REQUEST_RESPONSE

    email = Email.objects.create(
        user=request.user,
        to=brand_email,
        subject=subject,
        html_message=html_message,
        sender=request.user.username + "@creators.proeliumx.com",
        reply_to=request.user.email,
    )

    send_email_task.delay(email.id)
    return JsonResponse({"detail": "Email queued"}, status=status.HTTP_200_OK)
