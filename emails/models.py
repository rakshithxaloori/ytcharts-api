import uuid
from django.db import models

from authentication.models import User


class ChartPNG(models.Model):
    user = models.ForeignKey(User, related_name="chart_pngs", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    path = models.TextField()

    def __str__(self) -> str:
        return f"{self.path} || {self.user.email}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Chart PNGs"


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

    def __str__(self) -> str:
        return f"{self.subject} || {self.user.email}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Emails"
