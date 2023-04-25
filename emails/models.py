import uuid

from django.db import models
from django.utils import timezone

from authentication.models import User


class Email(models.Model):
    QUEUED = "q"
    # Resend types https://resend.com/docs/webhooks
    SENT = "s"
    DELIVERED = "d"
    DELIVERY_DELAYED = "dd"
    COMPLAINED = "c"
    BOUNCED = "b"
    OPENED = "o"
    CLICKED = "cl"

    STATUS_CHOICES = (
        (QUEUED, "Queued"),
        (SENT, "Sent"),
        (DELIVERED, "Delivered"),
        (DELIVERY_DELAYED, "Delivery Delayed"),
        (COMPLAINED, "Complained"),
        (BOUNCED, "Bounced"),
        (OPENED, "Opened"),
        (CLICKED, "Clicked"),
    )

    TEST = "t"
    LIVE = "l"
    TYPE_CHOICES = (
        (TEST, "Test"),
        (LIVE, "Live"),
    )

    RESEND = "r"
    SES = "s"
    CLIENT_CHOICES = (
        (RESEND, "Resend"),
        (SES, "SES"),
    )

    user = models.ForeignKey(User, related_name="emails", on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    to = models.EmailField()
    subject = models.CharField(max_length=255)
    html_message = models.TextField()
    plain_message = models.TextField()
    sender = models.EmailField()
    reply_to = models.EmailField()

    message_id = models.CharField(
        max_length=255, null=True, blank=True
    )  # Provided by the email service
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=QUEUED)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default=LIVE)
    client = models.CharField(max_length=1, choices=CLIENT_CHOICES, default=RESEND)

    def __str__(self) -> str:
        return f"To: {self.to} | {self.user.username} | Status: {self.status}"

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
    created_at = models.DateTimeField(default=timezone.now)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    path = models.CharField(max_length=1024)
    params = models.JSONField()

    def __str__(self) -> str:
        return f"{self.path} | {self.user.email}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Chart PNGs"


class EmailChartPNG(models.Model):
    email = models.ForeignKey(
        Email,
        related_name="e_email_chart_pngs",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
    )
    chart_png = models.ForeignKey(
        ChartPNG, related_name="c_email_chart_pngs", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(default=timezone.now)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self) -> str:
        return f"{self.email} | {self.chart_png}"

    class Meta:
        unique_together = ("email", "chart_png")
        verbose_name_plural = "Email Chart PNGs"
