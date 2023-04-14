import boto3

from django.conf import settings

from resend import Resend

resend_client = Resend(api_key=settings.RESEND_API_KEY)
ses_client = boto3.client(
    service_name="ses",
    aws_access_key_id=settings.AWS_SES_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SES_SECRET_ACCESS_KEY,
    region_name=settings.AWS_SES_REGION_NAME,
)


class EmailClient:
    RESEND = "resend"
    SES = "ses"


def send_email(
    to, subject, html_message, sender=None, reply_to=None, client=EmailClient.SES
):
    if client == EmailClient.RESEND:
        response = resend_client.send_email(
            to=to,
            sender=sender,
            subject=subject,
            html=html_message,
        )
        print("RESEND RESPONSE", response)
        return response["message_id"]
    elif client == EmailClient.SES:
        response = ses_client.send_email(
            Source=sender,
            Destination={
                "ToAddresses": [to],
                "CcAddresses": [reply_to] if reply_to else [],
            },
            Message={
                "Subject": {"Data": subject},
                "Body": {"Html": {"Data": html_message}},
            },
            ReplyToAddresses=[reply_to] if reply_to else [],
        )
        print("SES RESPONSE", response)
        return response["MessageId"]
