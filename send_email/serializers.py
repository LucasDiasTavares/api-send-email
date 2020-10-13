from rest_framework import serializers
from .models import Email


class SendEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = '__all__'
