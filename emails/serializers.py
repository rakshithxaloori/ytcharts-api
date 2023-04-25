from rest_framework.serializers import ModelSerializer


from emails.models import Email


class EmailShortSerializer(ModelSerializer):
    class Meta:
        model = Email
        fields = ["id", "subject", "to", "created_at", "status"]


class EmailLongSerializer(ModelSerializer):
    class Meta:
        model = Email
        fields = ["id", "subject", "to", "created_at", "status", "html_message"]
