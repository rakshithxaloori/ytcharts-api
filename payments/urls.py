from django.urls import path

from payments import views

urlpatterns = [
    path(
        "subscription/get/", views.has_active_subscription_view, name="get subscription"
    ),
    path("stripe/webhook/", views.stripe_webhook_view, name="stripe webhook"),
]
