import datetime

from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone

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
from authentication.google import get_google_user_info
from getabranddeal.utils import BAD_REQUEST_RESPONSE
from yt.yt_api_utils import get_yt_keys
from yt.models import FetchStatus, AccessKeys, Video, DailyViews
from yt.serializers import FetchStatusSerializer, VideoSerializer, DailyViewsSerializer
from yt.isocodes import ISO_CODES
from yt.tasks import fetch_daily_analytics_task


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def connect_yt_view(request):
    auth_code = request.data.get("auth_code", None)
    if auth_code is None:
        return BAD_REQUEST_RESPONSE
    keys_dict = get_yt_keys(auth_code)
    if keys_dict is None:
        return BAD_REQUEST_RESPONSE

    access_token = keys_dict.get("access_token", None)
    refresh_token = keys_dict.get("refresh_token", None)
    expires_in = keys_dict.get("expires_in", None)
    if None in [access_token, refresh_token, expires_in]:
        return BAD_REQUEST_RESPONSE

    expires_at = timezone.now().timestamp() + expires_in

    google_user_info = get_google_user_info(access_token)
    if google_user_info is None:
        return BAD_REQUEST_RESPONSE
    try:
        user = User.objects.get(email=google_user_info["email"])
        # Create FetchStatus object for the user if it doesn't exist
        FetchStatus.objects.get_or_create(user=user)
        AccessKeys.objects.update_or_create(
            user=user,
            defaults={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": expires_at,
                "is_refresh_valid": True,
            },
        )

        fetch_daily_analytics_task.delay(user.username)
        return JsonResponse(
            {
                "detail": "Successfully connected to YouTube",
            },
            status=status.HTTP_200_OK,
        )
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
    top_countries_codes = list(
        request.user.top_countries.values_list("country_code", flat=True)
    )
    top_countries_codes.append("##")
    payload_data = []
    for country_code in top_countries_codes:
        daily_views = (
            DailyViews.objects.filter(video=video, country_code=country_code)
            .order_by("-date")
            .exclude(Q(date__lt=start_date) | Q(date__gt=end_date))
        )
        daily_views_data = DailyViewsSerializer(daily_views, many=True).data
        daily_views_data.reverse()
        payload_data.append({"country_code": country_code, "views": daily_views_data})
    payload_data.sort(key=lambda x: x["country_code"])
    return JsonResponse(
        {
            "detail": "Daily views",
            "payload": {
                "video": VideoSerializer(video).data,
                "data": payload_data,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_status_view(request):
    user = request.user
    try:
        fetch_status = FetchStatus.objects.get(user=user)
    except FetchStatus.DoesNotExist:
        return BAD_REQUEST_RESPONSE

    fetch_status_data = FetchStatusSerializer(fetch_status).data
    return JsonResponse(
        {
            "detail": "Fetch status",
            "payload": fetch_status_data,
        },
        status=status.HTTP_200_OK,
    )
