import requests
import boto3

from botocore.exceptions import ClientError

from django.conf import settings

from emails.models import Email


def send_email(to, subject, html_message, sender, reply_to, client=Email.RESEND):
    if client == Email.RESEND:
        api_key = settings.RESEND_API_KEY
        endpoint = "https://api.resend.com/email"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        data = {
            "to": to,
            "subject": subject,
            "html": html_message,
            "from": sender,
            "reply_to": reply_to,
            "cc": reply_to,
        }
        response = requests.post(endpoint, headers=headers, json=data)
        if response.ok:
            json_data = response.json()
            print("RESEND RESPONSE", json_data)
            return json_data["id"]
        else:
            print("RESEND ERROR", response.text)
            return None
    elif client == Email.SES:
        try:
            ses_client = boto3.client(
                service_name="ses",
                aws_access_key_id=settings.AWS_SES_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SES_SECRET_ACCESS_KEY,
                region_name=settings.AWS_SES_REGION_NAME,
            )
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
        except ClientError as e:
            print("SES ERROR", e.response["Error"]["Message"])
            return None


def get_cdn_url(file_path):
    return f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_path}"
