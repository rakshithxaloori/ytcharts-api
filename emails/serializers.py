from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField


from authentication.models import User
from emails.models import Settings, Email


# Validate and save serializers
class EmailValidSerializer(ModelSerializer):
    user = PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Email
        fields = [
            "user",
            "to",
            "subject",
            "html_message",
            "plain_message",
            "sender",
            "reply_to",
            "type",
        ]


# Read-only serializers
class SettingsSerializer(ModelSerializer):
    class Meta:
        model = Settings
        fields = ["default_message", "default_subject"]
        read_only_fields = ["default_message", "default_subject"]


class EmailShortSerializer(ModelSerializer):
    class Meta:
        model = Email
        fields = ["id", "subject", "to", "created_at", "status"]
        read_only_fields = ["id", "subject", "to", "created_at", "status"]


class EmailLongSerializer(ModelSerializer):
    class Meta:
        model = Email
        fields = [
            "id",
            "subject",
            "to",
            "sender",
            "reply_to",
            "created_at",
            "status",
            "html_message",
        ]
        read_only_fields = [
            "id",
            "subject",
            "to",
            "sender",
            "reply_to",
            "created_at",
            "status",
            "html_message",
        ]
