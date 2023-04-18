from django.utils import timezone

from celery.schedules import crontab

from proeliumx.celery import app as celery_app

from emails.models import Email, ChartPNG, EmailChartPNG
from emails.utils import EmailClient, send_email


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # TODO test this
    sender.add_periodic_task(
        crontab(minute=0),
        delete_orphaned_chart_pngs_task.s(),
        name="delete orphaned chart pngs",
    )


@celery_app.task
def send_email_task(email_pk, client=EmailClient.RESEND):
    try:
        email = Email.objects.get(pk=email_pk)
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
        email.save(update_fields=["status"])
    except Email.DoesNotExist:
        pass


@celery_app.task
def delete_orphaned_chart_pngs_task():
    email_chart_pngs = EmailChartPNG.objects.filter(
        email=None, created_at__lt=timezone.now() - timezone.timedelta(hours=2)
    )
    ChartPNG.objects.filter(emailchartpng__in=email_chart_pngs).delete()
