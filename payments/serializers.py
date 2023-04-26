from rest_framework.serializers import ModelSerializer


from payments.models import Customer


class CustomerSerializer(ModelSerializer):
    class Meta:
        model = Customer
        fields = ["stripe_customer_id", "stripe_subscription_id"]
        read_only_fields = ["id", "stripe_customer_id", "stripe_subscription_id"]
