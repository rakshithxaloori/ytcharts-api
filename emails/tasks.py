from django.utils import timezone

from celery.schedules import crontab

from getabranddeal.celery import app as celery_app

from emails.models import Email, ChartPNG, EmailChartPNG
from emails.utils import send_email


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # TODO test this
    sender.add_periodic_task(
        crontab(minute=0),
        delete_orphaned_chart_pngs_task.s(),
        name="delete orphaned chart pngs",
    )
    # TODO periodic task that sends
    # emails that are queued


@celery_app.task
def send_email_task(email_pk, client=Email.RESEND):
    try:
        email = Email.objects.get(pk=email_pk)
        if email.status == Email.QUEUED:
            msg_id = send_email(
                to=email.to,
                subject=email.subject,
                html_message=email.html_message,
                sender=email.sender,
                reply_to=email.reply_to,
                client=client,
            )
            email.message_id = msg_id
            email.status = Email.SENT
            email.client = client
            email.save(update_fields=["message_id", "status", "client"])
    except Email.DoesNotExist:
        pass


@celery_app.task
def delete_orphaned_chart_pngs_task():
    chart_png_ids = EmailChartPNG.objects.filter(
        email=None, created_at__lt=timezone.now() - timezone.timedelta(hours=2)
    ).values_list("chart_png__id", flat=True)
    ChartPNG.objects.filter(id__in=chart_png_ids).delete()
