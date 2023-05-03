from rest_framework.serializers import ModelSerializer, SerializerMethodField


from yt.models import FetchStatus, Channel, Video, TopCountry, DailyViews, Demographics


class FetchStatusSerializer(ModelSerializer):
    class Meta:
        model = FetchStatus
        fields = [
            "is_fetching_at",
            "fetched_at",
            "is_daily_views_fetching",
            "is_demographics_fetching",
        ]


class ChannelSerializer(ModelSerializer):
    class Meta:
        model = Channel
        fields = ["channel_id", "title", "thumbnail", "subscriber_count"]


class VideoSerializer(ModelSerializer):
    channel = ChannelSerializer()
    id = SerializerMethodField()

    class Meta:
        model = Video
        fields = ["channel", "id", "title", "thumbnail", "published_at"]

    def get_id(self, obj):
        return obj.video_id


class TopCountrySerializer(ModelSerializer):
    class Meta:
        model = TopCountry
        fields = [
            "country_code",
            "views",
            "estimated_minutes_watched",
            "average_view_duration",
            "average_viewer_percentage",
            "subscribers_gained",
            "start_date",
            "end_date",
        ]


class DailyViewsSerializer(ModelSerializer):
    class Meta:
        model = DailyViews
        fields = ["date", "views"]


class DemographicsSerializer(ModelSerializer):
    class Meta:
        model = Demographics
        fields = ["age_group", "gender", "viewer_percentage", "start_date", "end_date"]
