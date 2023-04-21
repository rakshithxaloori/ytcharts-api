from celery.schedules import crontab


from proeliumx.celery import app as celery_app


from yt.models import AccessKeys, Channel, Video, DailyViews, DemographicsViews
from yt.yt_api_utils import (
    get_videos_yt_api,
    get_day_views_yt_api,
    get_demographics_views_yt_api,
)

VIDEOS_COUNT = 5


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # TODO test this
    sender.add_periodic_task(
        crontab(hour=0, minute=0),
        fetch_daily_analytics_task.s(),
        name="fetch daily analytics",
    )


@celery_app.task
def fetch_daily_analytics_task():
    # Fetch all recent videos
    # Fetch daily views with top countries of the latest 5 videos
    # Fetch demographics with top countries of the latest 5 videos
    pass


def fetch_latest_videos():
    for access_keys in AccessKeys.objects.all():
        username = access_keys.user.username
        videos = get_videos_yt_api(username, max_results=VIDEOS_COUNT)
        for video in videos:
            print(video)
            # TODO save video to db


def fetch_daily_views():
    for access_keys in AccessKeys.objects.all():
        username = access_keys.user.username
        for channel in Channel.objects.filter(user=access_keys.user):
            for video in channel.videos.order_by("-created_at")[:VIDEOS_COUNT]:
                video_id = video.video_id
                day_views = get_day_views_yt_api(username, video_id, country=None)
                print(day_views)


def fetch_demographics_views():
    for access_keys in AccessKeys.objects.all():
        username = access_keys.user.username
        for channel in Channel.objects.filter(user=access_keys.user):
            for video in channel.videos.order_by("-created_at")[:VIDEOS_COUNT]:
                video_id = video.video_id
                demographics_views = get_demographics_views_yt_api(
                    username, video_id, country=None
                )
                print(demographics_views)
