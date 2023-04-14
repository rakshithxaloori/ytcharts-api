from emails.models import Email
from emails.utils import EmailClient, send_email


def send_email_task(email_pk, client=EmailClient.SES):
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
