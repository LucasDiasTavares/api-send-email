from rest_framework import serializers
from send_email.models import Email


class SendEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = '__all__'
