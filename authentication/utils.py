from django.http import JsonResponse
from django.utils import timezone

from rest_framework import status

from knox.models import AuthToken


def token_response(user):
    token = AuthToken.objects.create(user)[1]
    # Change user's last login to current time
    user.last_login = timezone.now()
    user.save(update_fields=["last_login"])
    return JsonResponse(
        {
            "detail": "Logged in",
            "payload": {
                "token_key": token,
                "user": {
                    "username": user.username,
                    "picture": user.picture,
                },
            },
        },
        status=status.HTTP_200_OK,
    )
