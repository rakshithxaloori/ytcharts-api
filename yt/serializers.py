from rest_framework.serializers import ModelSerializer, SerializerMethodField


from yt.models import DailyViews


class DailyViewsSerializer(ModelSerializer):
    class Meta:
        model = DailyViews
        fields = ["date", "views"]
