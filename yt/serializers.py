from rest_framework.serializers import ModelSerializer


from yt.models import Video, DailyViews


class VideoSerializer(ModelSerializer):
    class Meta:
        model = Video
        fields = ["video_id", "title", "thumbnail", "published_at"]


class DailyViewsSerializer(ModelSerializer):
    class Meta:
        model = DailyViews
        fields = ["date", "views"]
