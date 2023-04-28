import requests

from django.conf import settings

from emails.models import Email


def send_email(
    to, subject, html_message, plain_message, sender, reply_to, client=Email.RESEND
):
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
            "text": plain_message,
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


def get_cdn_url(file_path):
    return f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_path}"
