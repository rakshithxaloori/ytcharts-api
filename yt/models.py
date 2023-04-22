import uuid
from django.db import models

from authentication.models import User


class Channel(models.Model):
    user = models.ForeignKey(User, related_name="channels", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    id = models.CharField(primary_key=True, max_length=24, blank=False, null=False)
    title = models.CharField(max_length=255, null=False, blank=False)
    thumbnail = models.URLField(null=False, blank=False)
    subscriber_count = models.PositiveIntegerField(null=False, blank=False, default=0)

    def __str__(self) -> str:
        return "{} || {} subscribers || {}".format(
            self.title, self.subscriber_count, self.user.email
        )


class Video(models.Model):
    channel = models.ForeignKey(
        Channel, related_name="videos", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    id = models.CharField(
        primary_key=True, editable=False, max_length=11, null=False, blank=False
    )
    title = models.CharField(max_length=100)
    thumbnail = models.URLField()
    description = models.TextField()

    def __str__(self) -> str:
        return "{} || {}".format(self.id, self.channel.title)


class AccessKeys(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="access_keys")
    created_at = models.DateTimeField(auto_now_add=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    access_token = models.CharField(max_length=2048)
    valid_till = models.PositiveIntegerField()
    refresh_token = models.CharField(max_length=512)
    is_refresh_valid = models.BooleanField(default=True)

    # Links
    # Token sizes - https://developers.google.com/identity/protocols/oauth2#size
    # Refresh tokens may expire
    # https://developers.google.com/identity/protocols/oauth2#expiration

    def __str__(self):
        return f"{self.user.username} | {self.is_refresh_valid}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Access Keys"


class DailyViews(models.Model):
    # X-axis - date
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="daily_views")
    video = models.ForeignKey(
        Video, on_delete=models.CASCADE, related_name="daily_views"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField()
    # https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
    # '##' for global views
    country_code = models.CharField(max_length=2)
    views = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} | {self.date}: {self.views}"

    class Meta:
        ordering = ["date"]
        verbose_name_plural = "Daily Views"


class DemographicsViews(models.Model):
    # X-axis - ageGroup,gender
    AGE_13_TO_17 = "age13-17"
    AGE_18_TO_24 = "age18-24"
    AGE_25_TO_34 = "age25-34"
    AGE_35_TO_44 = "age35-44"
    AGE_45_TO_54 = "age45-54"
    AGE_55_TO_64 = "age55-64"
    AGE_65_PLUS = "age65-"
    AGE_CHOICES = [
        (AGE_13_TO_17, "13-17"),
        (AGE_18_TO_24, "18-24"),
        (AGE_25_TO_34, "25-34"),
        (AGE_35_TO_44, "35-44"),
        (AGE_45_TO_54, "45-54"),
        (AGE_55_TO_64, "55-64"),
        (AGE_65_PLUS, "65-"),
    ]

    MALE = "m"
    FEMALE = "f"
    USER_UNSPECIFIED = "u"
    GENDER_CHOICES = (
        MALE,
        "Male",
        FEMALE,
        "Female",
        USER_UNSPECIFIED,
        "User Unspecified",
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="demographics_views"
    )
    video = models.ForeignKey(
        Video, on_delete=models.CASCADE, related_name="demographics_views"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
    # '##' for global views
    country_code = models.CharField(max_length=2)
    age_group = models.CharField(max_length=10, choices=AGE_CHOICES)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    viewer_percentage = models.FloatField()

    def __str__(self):
        return f"{self.user.username} | {self.age_group}: {self.viewer_percentage}"

    class Meta:
        ordering = ["age_group"]
        verbose_name_plural = "Demographics Views"
