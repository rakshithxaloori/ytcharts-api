from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view


from getabranddeal.utils import BAD_REQUEST_RESPONSE
from authentication.models import User
from yt.models import Video
from yt.serializers import (
    VideoSerializer,
    TopCountrySerializer,
    DailyViewsSerializer,
    DemographicsSerializer,
)
from authentication.serializers import ProfileSerializer


@api_view(["POST"])
def get_profile_view(request):
    num_days = 30
    username = request.data.get("username", None)
    video_id = request.data.get("video_id", None)
    if username is None:
        return BAD_REQUEST_RESPONSE

    try:
        user = User.objects.get(username=username)
        end_date = timezone.now().strftime("%Y-%m-%d")
        start_date = (timezone.now() - timezone.timedelta(days=num_days)).strftime(
            "%Y-%m-%d"
        )
        profile_data = ProfileSerializer(user).data

        # Get YouTube channel data
        if video_id is None:
            video = user.videos.order_by("-published_at").first()
        else:
            try:
                video = Video.objects.get(video_id=video_id, user=user)
            except Video.DoesNotExist:
                video = user.videos.order_by("-published_at").first()

        videos = user.videos.order_by("-published_at")[:3]
        videos_data = VideoSerializer(videos, many=True).data

        top_countries = user.top_countries.all().order_by("-views")
        top_countries_data = TopCountrySerializer(top_countries, many=True).data

        top_countries_codes = list(top_countries.values_list("country_code", flat=True))
        top_countries_codes.append("##")

        daily_views_data = {}
        demographics_data = {}

        for top_country_code in top_countries_codes:
            country_code = top_country_code
            dw = (
                user.daily_views.filter(country_code=country_code, video=video)
                .exclude(Q(date__lt=start_date) | Q(date__gt=end_date))
                .order_by("date")
            )
            dw_data = DailyViewsSerializer(dw, many=True).data
            daily_views_data[country_code] = dw_data

            dv = user.u_demographics.filter(country_code=country_code, video=video)
            dv_data = DemographicsSerializer(dv, many=True).data
            demographics_data[country_code] = dv_data

        return JsonResponse(
            {
                "detail": f"{user.username}'s profile data",
                "payload": {
                    "profile": profile_data,
                    "video": VideoSerializer(video).data,
                    "top_countries": top_countries_data,
                    "daily_views": daily_views_data,
                    "demographics": demographics_data,
                    "videos": videos_data,
                },
            },
            status=status.HTTP_200_OK,
        )

    except User.DoesNotExist:
        return BAD_REQUEST_RESPONSE
