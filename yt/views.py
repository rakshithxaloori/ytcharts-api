import datetime

from django.http import JsonResponse
from django.db.models import Q

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)


from knox.auth import TokenAuthentication
from knox.models import AuthToken


from authentication.models import User
from authentication.utils import token_response
from authentication.google import get_google_user_info
from getabranddeal.utils import BAD_REQUEST_RESPONSE
from yt.yt_api_utils import get_access_token
from yt.models import AccessKeys, Video, DailyViews
from yt.serializers import VideoSerializer, DailyViewsSerializer
from yt.isocodes import ISO_CODES
from yt.tasks import fetch_daily_analytics_task


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
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
        AccessKeys.objects.update_or_create(
            user=user,
            defaults={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": expires_at,
                "is_refresh_valid": True,
            },
        )

        AuthToken.objects.filter(user=user).delete()

        fetch_daily_analytics_task.delay(user.username)
        return token_response(user)
    except User.DoesNotExist:
        return BAD_REQUEST_RESPONSE


@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_views_view(request):
    video_id = request.data.get("video_id", None)
    country_code = request.data.get("country_code", "##")
    # num_days = request.data.get("num_days", 30)
    num_days = 30

    if country_code != "##" and country_code not in ISO_CODES.keys():
        return BAD_REQUEST_RESPONSE
    user = request.user
    try:
        video = Video.objects.get(user=user, video_id=video_id)
    except Video.DoesNotExist:
        video = user.videos.order_by("-published_at").first()

    end_date = datetime.datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.datetime.now() - datetime.timedelta(days=num_days)).strftime(
        "%Y-%m-%d"
    )
    daily_views = (
        DailyViews.objects.filter(video=video, country_code=country_code)
        .order_by("-date")
        .exclude(Q(date__lt=start_date) | Q(date__gt=end_date))
    )
    daily_views_data = DailyViewsSerializer(daily_views, many=True).data
    daily_views_data.reverse()
    return JsonResponse(
        {
            "detail": "Daily views",
            "payload": {
                "video": VideoSerializer(video).data,
                "data": {"country_code": country_code, "views": daily_views_data},
            },
        },
        status=status.HTTP_200_OK,
    )
