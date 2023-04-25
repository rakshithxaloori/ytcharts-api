from django.urls import path

from emails import views

urlpatterns = [
    path("settings/get/", views.get_settings_view, name="get settings"),
    path("emails/get/", views.get_emails_view, name="get emails"),
    path("email/get/", views.get_email_view, name="get email"),
    path("image/presigned/", views.get_presigned_post_view, name="get presigned post"),
    path("email/post/", views.post_email_view, name="post email"),
    path("resend/webhook/", views.resend_webhook_view, name="resend webhook"),
]
