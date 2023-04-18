import uuid
from django.db import models

from authentication.models import User


class Email(models.Model):
    QUEUED = "q"
    SENT = "s"
    DELIVERED = "d"
    BOUNCED = "b"
    STATUS_CHOICES = (
        (QUEUED, "Queued"),
        (SENT, "Sent"),
        (DELIVERED, "Delivered"),
        (BOUNCED, "Bounced"),
    )

    TEST = "t"
    LIVE = "l"
    TYPE_CHOICES = (
        (TEST, "Test"),
        (LIVE, "Live"),
    )

    user = models.ForeignKey(User, related_name="emails", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    to = models.EmailField()
    subject = models.CharField(max_length=255)
    html_message = models.TextField()
    sender = models.EmailField()
    reply_to = models.EmailField()

    message_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=QUEUED)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default=LIVE)

    def __str__(self) -> str:
        return f"{self.subject} || {self.user.email}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Emails"


class ChartPNG(models.Model):
    user = models.ForeignKey(User, related_name="chart_pngs", on_delete=models.CASCADE)
    emails = models.ManyToManyField(
        Email,
        related_name="chart_pngs",
        through="EmailChartPNG",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    path = models.CharField(max_length=1024)
    params = models.JSONField()

    def __str__(self) -> str:
        return f"{self.path} || {self.user.email}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Chart PNGs"


class EmailChartPNG(models.Model):
    email = models.ForeignKey(
        Email, on_delete=models.CASCADE, null=True, blank=True, default=None
    )
    chart_png = models.ForeignKey(ChartPNG, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        unique_together = ("email", "chart_png")
        verbose_name_plural = "Email Chart PNGs"
