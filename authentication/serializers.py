from rest_framework.serializers import ModelSerializer


from authentication.models import User


class ProfileSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "picture"]
