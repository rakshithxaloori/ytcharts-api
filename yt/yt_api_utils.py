import requests
import datetime

from django.conf import settings
from django.utils import timezone

from yt.models import AccessKeys
from proeliumx.utils import get_now_timestamp


yt_reports_endpoint = "https://youtubeanalytics.googleapis.com/v2/reports"


def get_day_views_yt_api(username, video_id, country=None):
    # Set the start and end dates for the report (last 3 months)
    end_date = datetime.datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.datetime.now() - datetime.timedelta(days=90)).strftime(
        "%Y-%m-%d"
    )

    # Set the API parameters
    params = {
        "ids": "channel==MINE",
        "metrics": "views",
        "dimensions": "day",
        "startDate": start_date,
        "endDate": end_date,
        "filters": f"video=={video_id}"
        if country is None
        else f"video=={video_id};country=={country}",
    }

    # Set the authorization header with the access token
    access_token = get_access_token(username)
    headers = {"Authorization": f"Bearer {access_token}"}

    # Make the API request
    response = requests.get(yt_reports_endpoint, params=params, headers=headers)

    # Parse the response and extract the view count
    if response.ok:
        data = response.json()
        return data
    else:
        print(f"Error retrieving data: {response.status_code} - {response.reason}")
        return None


def get_demographics_views_yt_api(username, channel_id, country=None):
    end_date = datetime.datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.datetime.now() - datetime.timedelta(days=90)).strftime(
        "%Y-%m-%d"
    )
    params = {
        "ids": f"channel=={channel_id}",
        "metrics": "viewerPercentage",
        "dimensions": "ageGroup,gender",
        "startDate": start_date,
        "endDate": end_date,
        "sort": "gender,ageGroup",
    }
    if country is not None:
        params["filters"] = f"country=={country}"

    # Set the headers with the access_token
    access_token = get_access_token(username)
    headers = {"Authorization": f"Bearer {access_token}"}

    # Send the request and get the response
    response = requests.get(yt_reports_endpoint, params=params, headers=headers)
    if response.ok:
        data = response.json()
        return data
    else:
        print(f"Error retrieving data: {response.status_code} - {response.reason}")
        return None


##########################################################
# Using YouTube OAuth
def get_access_token(username):
    try:
        # Check access token expiry
        yt_keys = AccessKeys.objects.get(user__username=username, is_refresh_valid=True)
        timestamp_now = get_now_timestamp()
        if timestamp_now < yt_keys.valid_till:
            return yt_keys.access_token
        else:
            # Refresh access token
            uri = "https://oauth2.googleapis.com/token"
            post_data = {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "refresh_token": yt_keys.refresh_token,
                "grant_type": "refresh_token",
            }

            response = requests.post(url=uri, data=post_data)
            if response.ok:
                json_data = response.json()
                access_token = json_data["access_token"]
                expires_in = json_data["expires_in"]
                yt_keys.access_token = access_token
                yt_keys.valid_till = (
                    timezone.now() + timezone.timedelta(seconds=expires_in)
                ).timestamp()
                yt_keys.save(update_fields=["access_token", "valid_till"])
                return access_token
            else:
                print("Refresh Token expired")
                yt_keys.is_refresh_valid = False
                yt_keys.save(update_fields=["is_refresh_valid"])
                return None
    except AccessKeys.DoesNotExist:
        print("AccessKeys doesn't exist")
        return None


##########################################################
# Using YouTube API Key
API_KEY = settings.GOOGLE_API_KEY


def get_yt_channels_yt_api(access_token: str = None):
    if access_token is None:
        return None

    endpoint = "https://www.googleapis.com/youtube/v3/channels"
    params = {"part": "snippet,statistics", "mine": "true", "maxResults": "50"}
    headers = {
        "Authorization": "Bearer {}".format(access_token),
    }
    response = requests.get(endpoint, params=params, headers=headers)
    if response.ok:
        json_data = response.json()
        return json_data.get("items", None)
    else:
        print("get_yt_channels_info ERROR", response.status_code, response.reason)
        return None


def get_videos_yt_api(username, max_results=5):
    access_token = get_access_token(username)
    if access_token is None:
        return None
    uri = "https://youtube.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "channelType": "any",
        "forMine": True,
        "maxResults": max_results,
        "order": "date",
        "type": "video",
        "key": API_KEY,
    }
    headers = {
        "Authorization": "Bearer {}".format(access_token),
        "Content-Type": "application/json",
    }
    response = requests.get(uri, params=params, headers=headers)
    if response.ok:
        json_data = response.json()
        return json_data["items"]
    else:
        return None
