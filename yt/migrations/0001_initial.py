# Generated by Django 4.2 on 2023-04-24 07:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Channel",
            fields=[
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("channel_id", models.CharField(max_length=24)),
                ("title", models.CharField(max_length=255)),
                ("thumbnail", models.URLField()),
                ("subscriber_count", models.PositiveIntegerField(default=0)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="channels",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Video",
            fields=[
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("video_id", models.CharField(max_length=11)),
                ("title", models.CharField(max_length=100)),
                ("thumbnail", models.URLField()),
                ("description", models.TextField()),
                ("published_at", models.DateTimeField()),
                (
                    "channel",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="videos",
                        to="yt.channel",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="videos",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DemographicsViews",
            fields=[
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("country_code", models.CharField(max_length=2)),
                (
                    "age_group",
                    models.CharField(
                        choices=[
                            ("age13-17", "13-17"),
                            ("age18-24", "18-24"),
                            ("age25-34", "25-34"),
                            ("age35-44", "35-44"),
                            ("age45-54", "45-54"),
                            ("age55-64", "55-64"),
                            ("age65-", "65-"),
                        ],
                        max_length=10,
                    ),
                ),
                (
                    "gender",
                    models.CharField(
                        choices=[
                            ("m", "Male"),
                            ("f", "Female"),
                            ("u", "User Unspecified"),
                        ],
                        max_length=1,
                    ),
                ),
                ("viewer_percentage", models.FloatField()),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="demographics_viewer_percentage",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "video",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="demographics_viewer_percentage",
                        to="yt.video",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Demographics Views",
                "ordering": ["age_group"],
            },
        ),
        migrations.CreateModel(
            name="DailyViews",
            fields=[
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("date", models.DateField()),
                ("country_code", models.CharField(max_length=2)),
                ("views", models.PositiveBigIntegerField(default=0)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="daily_views",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "video",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="daily_views",
                        to="yt.video",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Daily Views",
                "ordering": ["date"],
            },
        ),
        migrations.CreateModel(
            name="AccessKeys",
            fields=[
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("access_token", models.CharField(max_length=2048)),
                ("valid_till", models.PositiveIntegerField()),
                ("refresh_token", models.CharField(max_length=512)),
                ("is_refresh_valid", models.BooleanField(default=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="access_keys",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Access Keys",
                "ordering": ["-created_at"],
            },
        ),
    ]
