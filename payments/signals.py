import stripe

from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from django.core.files.storage import default_storage


from payments.models import Subscription

stripe.api_key = settings.STRIPE_API_KEY


# Delete stripe subscription when Subscription instance is deleted
@receiver(post_delete, sender=Subscription)
def delete_stripe_subscription(sender, instance, **kwargs):
    stripe.Subscription.delete(instance.stripe_subscription_id)
