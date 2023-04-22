from celery.schedules import crontab


from getabranddeal.celery import app as celery_app


from yt.models import AccessKeys, Channel, Video, DailyViews, DemographicsViews
from yt.yt_api_utils import (
    get_yt_channels_yt_api,
    get_videos_yt_api,
    get_day_views_yt_api,
    get_demographics_views_yt_api,
)
from yt.instances_utils import create_delete_update_yt_channels

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
def fetch_daily_analytics_task(username=None):
    # Fetch all recent videos
    fetch_latest_videos(username)
    # Fetch daily views with top countries of the latest 5 videos
    fetch_daily_views.delay(username)
    # Fetch demographics with top countries of the latest 5 videos
    fetch_demographics_views.delay(username)


def fetch_latest_videos(username=None):
    if username is None:
        access_keys_list = AccessKeys.objects.all()
    else:
        access_keys_list = AccessKeys.objects.filter(user__username=username)
    for access_keys in access_keys_list:
        username = access_keys.user.username
        yt_channels = get_yt_channels_yt_api(access_keys.access_token)
        create_delete_update_yt_channels(access_keys.user, yt_channels)
        videos = get_videos_yt_api(username, max_results=VIDEOS_COUNT)
        for video in videos:
            Video.objects.update_or_create(
                id=video["id"]["videoId"],
                defaults={
                    "id": video["id"]["videoId"],
                    "channel_id": video["snippet"]["channelId"],
                    "title": video["snippet"]["title"],
                    "thumbnail": video["snippet"]["thumbnails"]["default"]["url"],
                    "description": video["snippet"]["description"],
                },
            )


@celery_app.task
def fetch_daily_views(username=None):
    if username is None:
        access_keys_list = AccessKeys.objects.all()
    else:
        access_keys_list = AccessKeys.objects.filter(user__username=username)
    for access_keys in access_keys_list:
        username = access_keys.user.username
        for channel in Channel.objects.filter(user=access_keys.user):
            for video in channel.videos.order_by("-created_at")[:VIDEOS_COUNT]:
                # TODO country_code
                country_code = "##"
                day_views = get_day_views_yt_api(username, video.id, country_code)
                if "rows" not in day_views:
                    continue
                for row in day_views["rows"]:
                    if len(row) == 2:
                        DailyViews.objects.update_or_create(
                            user=access_keys.user,
                            video=video,
                            country_code=country_code,
                            date=row[0],
                            defaults={
                                "user": access_keys.user,
                                "video": video,
                                "date": country_code,
                                "views": row[1],
                            },
                        )


@celery_app.task
def fetch_demographics_views(username=None):
    if username is None:
        access_keys_list = AccessKeys.objects.all()
    else:
        access_keys_list = AccessKeys.objects.filter(user__username=username)
    for access_keys in access_keys_list:
        username = access_keys.user.username
        for channel in Channel.objects.filter(user=access_keys.user):
            for video in channel.videos.order_by("-created_at")[:VIDEOS_COUNT]:
                country_code = "##"
                demographics_views = get_demographics_views_yt_api(
                    username, video.id, country_code
                )
                if "rows" not in demographics_views:
                    continue
                for row in demographics_views["rows"]:
                    if len(row) == 3:
                        DemographicsViews.objects.update_or_create(
                            user=access_keys.user,
                            video=video,
                            country_code=country_code,
                            age_group=row[0],
                            defaults={
                                "user": access_keys.user,
                                "video": video,
                                "country_code": country_code,
                                "age_group": row[0],
                                "gender": row[1],
                                "viewer_percentage": row[2],
                            },
                        )


# print(day_views)
# {
#     "kind": "youtubeAnalytics#resultTable",
#     "columnHeaders": [
#         {
#             "name": "day",
#             "columnType": "DIMENSION",
#             "dataType": "STRING",
#         },
#         {
#             "name": "views",
#             "columnType": "METRIC",
#             "dataType": "INTEGER",
#         },
#     ],
#     "rows": [["2023-03-11", 1]],
# }

# print(demographics_views)
# {
#     "kind": "youtubeAnalytics#resultTable",
#     "columnHeaders": [
#         {
#             "name": "ageGroup",
#             "columnType": "DIMENSION",
#             "dataType": "STRING",
#         },
#         {
#             "name": "gender",
#             "columnType": "DIMENSION",
#             "dataType": "STRING",
#         },
#         {
#             "name": "viewerPercentage",
#             "columnType": "METRIC",
#             "dataType": "FLOAT",
#         },
#     ],
#     "rows": [],
# }