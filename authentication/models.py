from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    DEFAULT_COUNTRY_CODE = "###"
    picture = models.URLField(null=True, blank=True)
    country_code = models.CharField(max_length=3, default=DEFAULT_COUNTRY_CODE)
    last_open = models.DateTimeField(default=timezone.now)

    def __str__(self):
        days_diff = (timezone.now() - self.last_open).days
        if self.is_staff:
            return self.username
        else:
            return "{} {} || active {} days ago".format(
                self.first_name, self.last_name, days_diff
            )

    class Meta:
        ordering = ["-last_open"]
