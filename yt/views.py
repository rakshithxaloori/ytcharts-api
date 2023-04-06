from django.http import JsonResponse
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)

from rest_framework_api_key.permissions import HasAPIKey

from knox.auth import TokenAuthentication
from knox.models import AuthToken


from authentication.models import User
from authentication.utils import token_response
from authentication.google import get_google_user_info
from proeliumx.utils import BAD_REQUEST_RESPONSE
from yt.yt_api_utils import get_access_token, get_yt_channels_info
from yt.instances_utils import (
    create_or_update_yt_keys,
    create_delete_update_yt_channels,
)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def check_connected_view(request):
    return JsonResponse(
        {
            "detail": "YouTube connected",
            "payload": {
                "is_connected": get_access_token(request.user.username) is not None
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasAPIKey])
def connect_yt_view(request):
    access_token = request.data.get("access_token", None)
    refresh_token = request.data.get("refresh_token", None)
    expires_at = request.data.get("expires_at", None)

    if None in [access_token, refresh_token, expires_at]:
        return BAD_REQUEST_RESPONSE

    google_user_info = get_google_user_info(access_token)
    if google_user_info is None:
        return BAD_REQUEST_RESPONSE
    try:
        user = User.objects.get(username=google_user_info["id"])
        yt_channels = get_yt_channels_info(access_token)

        if yt_channels is None:
            return BAD_REQUEST_RESPONSE

        create_or_update_yt_keys(user, access_token, refresh_token, expires_at)
        create_delete_update_yt_channels(user, yt_channels)

        AuthToken.objects.filter(user=user).delete()
        return token_response(user)
    except User.DoesNotExist:
        return BAD_REQUEST_RESPONSE
