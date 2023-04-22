from django.http import JsonResponse
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)


from knox.auth import TokenAuthentication


from authentication.models import User
from authentication.utils import token_response
from authentication.google import get_google_user_info
from getabranddeal.utils import BAD_REQUEST_RESPONSE, get_country_code


@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def signout_view(request):
    # Delete auth token
    request._auth.delete()
    return JsonResponse({"detail": "Logged out"}, status=status.HTTP_200_OK)


@api_view(["POST"])
def signin_view(request):
    access_token = request.data.get("access_token", None)
    refresh_token = request.data.get("refresh_token", None)
    expires_at = request.data.get("expires_at", None)

    if None in [access_token, refresh_token, expires_at]:
        return BAD_REQUEST_RESPONSE

    user_info = get_google_user_info(access_token=access_token)
    if user_info is None:
        return BAD_REQUEST_RESPONSE

    try:
        # Check if user is registered
        user = User.objects.get(email=user_info["email"])
    except User.DoesNotExist:
        # Create User
        user_country_code = get_country_code(
            request.META.get("HTTP_X_FORWARDED_FOR"),
            request.META.get("REMOTE_ADDR"),
        )
        user = User.objects.create(
            username=user_info["id"],
            email=user_info["email"],
            first_name=user_info["given_name"],
            last_name=user_info["family_name"],
            picture=user_info["picture"],
            country_code=user_country_code,
        )
        user.set_unusable_password()

    return token_response(user)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def last_open_view(request):
    user = request.user
    user.last_open = timezone.now()
    user.save(update_fields=["last_open"])
    return JsonResponse({"detail": "last_open saved!"}, status=status.HTTP_200_OK)
