import datetime

from celery.schedules import crontab


from getabranddeal.celery import app as celery_app

from yt.models import (
    AccessKeys,
    Channel,
    Video,
    TopCountry,
    DailyViews,
    DemographicsViews,
)
from yt.yt_api_utils import (
    get_yt_channels_yt_api,
    get_videos_yt_api,
    get_top_countries_yt_api,
    get_day_views_yt_api,
    get_demographics_viewer_perc_yt_api,
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
def fetch_daily_analytics_task(username=None):
    # Update channels
    update_channels(username)
    # Fetch all recent videos
    fetch_latest_videos(username)
    # Get top countries
    fetch_top_countries(username)
    # Fetch daily views
    fetch_daily_views.delay(username)
    # Fetch demographics
    fetch_demographics_views.delay(username)


def update_channels(username=None):
    if username is None:
        access_keys_list = AccessKeys.objects.all()
    else:
        access_keys_list = AccessKeys.objects.filter(user__username=username)
    for access_keys in access_keys_list:
        user = access_keys.user
        yt_channels = get_yt_channels_yt_api(user.username)
        new_channel_ids = [yt_ch["id"] for yt_ch in yt_channels]

        # Delete
        for channel in Channel.objects.filter(user=user):
            if channel.channel_id not in new_channel_ids:
                channel.delete()

        # Create or update
        for yt_channel in yt_channels:
            Channel.objects.update_or_create(
                user=user,
                channel_id=yt_channel["id"],
                defaults={
                    "title": yt_channel["snippet"]["title"],
                    "thumbnail": yt_channel["snippet"]["thumbnails"]["default"]["url"],
                    "subscriber_count": yt_channel["statistics"]["subscriberCount"],
                },
            )


def fetch_latest_videos(username=None):
    if username is None:
        access_keys_list = AccessKeys.objects.all()
    else:
        access_keys_list = AccessKeys.objects.filter(user__username=username)
    for access_keys in access_keys_list:
        user = access_keys.user
        videos = get_videos_yt_api(user.username, max_results=VIDEOS_COUNT)
        for video in videos:
            channel = Channel.objects.get(channel_id=video["snippet"]["channelId"])
            Video.objects.update_or_create(
                user=user,
                video_id=video["id"]["videoId"],
                channel=channel,
                defaults={
                    "title": video["snippet"]["title"],
                    "thumbnail": video["snippet"]["thumbnails"]["default"]["url"],
                    "description": video["snippet"]["description"],
                    "published_at": video["snippet"]["publishedAt"],
                },
            )


def fetch_top_countries(username=None):
    if username is None:
        access_keys_list = AccessKeys.objects.all()
    else:
        access_keys_list = AccessKeys.objects.filter(user__username=username)
    end_date = datetime.datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.datetime.now() - datetime.timedelta(days=90)).strftime(
        "%Y-%m-%d"
    )
    for access_keys in access_keys_list:
        user = access_keys.user
        top_countries = get_top_countries_yt_api(user.username)
        for row in top_countries["rows"]:
            if len(row) == 6:
                TopCountry.objects.update_or_create(
                    user=user,
                    country_code=row[0],
                    defaults={
                        "views": row[1],
                        "estimated_minutes_watched": row[2],
                        "average_view_duration": row[3],
                        "average_viewer_percentage": row[4],
                        "subscribers_gained": row[5],
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                )


@celery_app.task
def fetch_daily_views(username=None):
    if username is None:
        access_keys_list = AccessKeys.objects.all()
    else:
        access_keys_list = AccessKeys.objects.filter(user__username=username)
    for access_keys in access_keys_list:
        user = access_keys.user
        for channel in Channel.objects.filter(user=user):
            for video in channel.videos.order_by("-published_at")[:VIDEOS_COUNT]:
                top_countries_codes = list(
                    TopCountry.objects.filter(user=user).values_list(
                        "country_code", flat=True
                    )
                )
                top_countries_codes.append("##")
                for top_country_code in top_countries_codes:
                    day_views = get_day_views_yt_api(
                        user.username, video.video_id, top_country_code
                    )
                    if day_views is None or "rows" not in day_views:
                        continue
                    for row in day_views["rows"]:
                        if len(row) == 2:
                            DailyViews.objects.update_or_create(
                                user=user,
                                video=video,
                                country_code=top_country_code,
                                date=row[0],
                                defaults={"views": row[1]},
                            )


@celery_app.task
def fetch_demographics_views(username=None):
    if username is None:
        access_keys_list = AccessKeys.objects.all()
    else:
        access_keys_list = AccessKeys.objects.filter(user__username=username)
    end_date = datetime.datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.datetime.now() - datetime.timedelta(days=90)).strftime(
        "%Y-%m-%d"
    )
    for access_keys in access_keys_list:
        user = access_keys.user
        for channel in Channel.objects.filter(user=user):
            for video in channel.videos.order_by("-published_at")[:VIDEOS_COUNT]:
                top_countries_codes = list(
                    TopCountry.objects.filter(user=user).values_list(
                        "country_code", flat=True
                    )
                )
                top_countries_codes.append("##")
                for top_country_code in top_countries_codes:
                    country_code = top_country_code
                    demographics_views = get_demographics_viewer_perc_yt_api(
                        user.username, video.video_id, top_country_code
                    )
                    if demographics_views is None or "rows" not in demographics_views:
                        continue
                    for row in demographics_views["rows"]:
                        if len(row) == 3:
                            yt_gender = row[1]
                            if yt_gender == "female":
                                yt_gender = DemographicsViews.FEMALE
                            elif yt_gender == "male":
                                yt_gender = DemographicsViews.MALE
                            else:
                                yt_gender = DemographicsViews.USER_UNSPECIFIED
                            DemographicsViews.objects.update_or_create(
                                user=user,
                                video=video,
                                country_code=top_country_code,
                                age_group=row[0],
                                gender=yt_gender,
                                defaults={
                                    "viewer_percentage": row[2],
                                    "start_date": start_date,
                                    "end_date": end_date,
                                },
                            )
