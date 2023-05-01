import datetime
import stripe

from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)

from knox.auth import TokenAuthentication


from authentication.models import User
from payments.models import Customer


stripe.api_key = settings.STRIPE_API_KEY
STRIPE_WEBHOOK_SECRET = settings.STRIPE_WEBHOOK_SECRET


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def has_active_subscription_view(request):
    try:
        customer = Customer.objects.get(user=request.user)
        return JsonResponse(
            {
                "detail": "Subscription",
                "payload": {
                    "is_active": customer.current_period_end > timezone.now(),
                },
            }
        )
    except Customer.DoesNotExist:
        return JsonResponse(
            {
                "detail": "Subscription",
                "payload": {
                    "is_active": False,
                },
            }
        )


@csrf_exempt
def stripe_webhook_view(request):
    try:
        signature = request.headers["STRIPE_SIGNATURE"]
        event = stripe.Webhook.construct_event(
            payload=request.body, sig_header=signature, secret=STRIPE_WEBHOOK_SECRET
        )
        # Get the type of webhook poll sent - used to check the status of PaymentIntents.
        poll_type = event.type
        subscription = event.data.object
    except Exception:
        print("Error while parsing webhook.")
        return HttpResponse(status=400)

    # Handle the event
    print("Event type: ", poll_type)
    if (
        poll_type == "customer.subscription.updated"
        and isinstance(subscription, stripe.Subscription)
        and subscription.status == "active"
    ):
        # Get customer email
        customer = stripe.Customer.retrieve(subscription.customer)
        try:
            email = customer.email
            user = User.objects.get(email=email)

            # Convert current_period_end to datetime
            current_period_end = timezone.make_aware(
                datetime.datetime.fromtimestamp(subscription.current_period_end)
            )
            Customer.objects.update_or_create(
                user=user,
                defaults={
                    "stripe_customer_id": customer.id,
                    "stripe_subscription_id": subscription.id,
                    "current_period_end": current_period_end,
                },
            )
        except User.DoesNotExist:
            # Cancel subscription
            stripe.Subscription.delete(subscription.id)
            return HttpResponse(status=200)

    elif poll_type == "customer.subscription.deleted":
        print(subscription)
        # TODO set is_active to False

    return HttpResponse(status=200)
