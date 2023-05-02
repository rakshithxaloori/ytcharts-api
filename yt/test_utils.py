import random
from datetime import date, timedelta

from yt.models import Demographics

NUM_DAYS = 90

dayViewsResultTable = {
    "kind": "youtubeAnalytics#resultTable",
    "columnHeaders": [
        {"name": "day", "columnType": "DIMENSION", "dataType": "STRING"},
        {"name": "views", "columnType": "METRIC", "dataType": "INTEGER"},
    ],
    "rows": [],
}


def test_get_day_views_yt_api():
    today = date.today()
    for i in range(NUM_DAYS):
        row_date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        row_views = random.randint(1, 1000)
        dayViewsResultTable["rows"].append([row_date, row_views])

    return dayViewsResultTable


demographicsViewerPercResultTable = {
    "kind": "youtubeAnalytics#resultTable",
    "columnHeaders": [
        {"name": "ageGroup", "columnType": "DIMENSION", "dataType": "STRING"},
        {"name": "gender", "columnType": "DIMENSION", "dataType": "STRING"},
        {"name": "viewerPercentage", "columnType": "METRIC", "dataType": "FLOAT"},
    ],
    "rows": [],
}


def test_get_demographics_viewer_perc_yt_api():
    age_groups = [age_group[0] for age_group in Demographics.AGE_CHOICES]
    genders = ["male", "female", "user_specified"]
    total_percentage = 0

    for age_group in age_groups:
        for gender in genders:
            viewer_percentage = round(random.uniform(0, 100), 2)
            demographicsViewerPercResultTable["rows"].append(
                [age_group, gender, viewer_percentage]
            )
            total_percentage += viewer_percentage

    # Normalize viewer percentages if the total is not equal to 100
    if total_percentage != 100:
        for row in demographicsViewerPercResultTable["rows"]:
            row[2] = (row[2] / total_percentage) * 100

    return demographicsViewerPercResultTable
