from yt.models import Channel, AccessKeys, Video


##########################################################
def create_or_update_yt_keys(user, access_token, refresh_token, valid_till):
    yt_keys, created = AccessKeys.objects.update_or_create(
        user=user,
        defaults={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "valid_till": valid_till,
            "is_refresh_valid": True,
        },
    )


def create_delete_update_yt_channels(user, channels):
    new_channel_ids = [ch["id"] for ch in channels]
    # Delete
    for channel in Channel.objects.filter(user=user):
        if channel.id not in new_channel_ids:
            channel.delete()

    # Create or update
    for channel in channels:
        channel_id = channel["id"]
        channel_title = channel["snippet"]["title"]
        channel_thumbnail = channel["snippet"]["thumbnails"]["default"]["url"]
        subscriber_count = channel["statistics"]["subscriberCount"]

        Channel.objects.update_or_create(
            user=user,
            id=channel_id,
            defaults={
                "id": channel_id,
                "user": user,
                "title": channel_title,
                "thumbnail": channel_thumbnail,
                "subscriber_count": subscriber_count,
            },
        )


def get_or_create_video(video_id, channel_id):
    if None in [video_id, channel_id]:
        return None, None
    try:
        channel = Channel.objects.get(id=channel_id)
    except Channel.DoesNotExist:
        return None, None
    video, created = Video.objects.get_or_create(id=video_id, channel=channel)
    if created:
        snippet = get_video_yt_api(channel.user.username, video_id)
        title = snippet["snippet"]["title"]
        thumbnails = snippet["snippet"]["thumbnails"]
        thumbnail_url = None
        if "high" in thumbnails:
            thumbnail_url = thumbnails["high"]["url"]
        else:
            thumbnail_url = thumbnails["default"]["url"]
        video.title = title
        video.thumbnail = thumbnail_url
        video.save(update_fields=["title", "thumbnail"])
    return video, created
