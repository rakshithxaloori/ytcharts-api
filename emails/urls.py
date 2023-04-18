from django.urls import path

from emails import views

urlpatterns = [
    path("image/presigned/", views.get_presigned_post_view, name="get presigned post"),
    path("email/post/", views.post_email_view, name="post email"),
    path("resend/webhook/", views.resend_webhook_view, name="resend webhook"),
]
