from rest_framework.serializers import ModelSerializer


from emails.models import Settings, Email


class SettingsSerializer(ModelSerializer):
    class Meta:
        model = Settings
        fields = ["default_message", "default_subject"]


class EmailShortSerializer(ModelSerializer):
    class Meta:
        model = Email
        fields = ["id", "subject", "to", "created_at", "status"]


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
