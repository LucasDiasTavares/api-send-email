from django.conf import settings
from rest_framework.exceptions import UnsupportedMediaType, NotAcceptable
from rest_framework import serializers
from .models import Email


class SendEmailSerializer(serializers.ModelSerializer):
    subject = serializers.CharField(max_length=256)
    content = serializers.CharField(max_length=65535)
    emailFrom = serializers.EmailField(max_length=256)
    emailTo = serializers.EmailField(max_length=256)
    task_id = serializers.CharField(allow_blank=True, allow_null=True)

    class Meta:
        model = Email
        exclude = ('updated_at', )

    def validate(self, attrs):
        file = attrs.get('file', '')
        if file:
            if file.content_type in settings.CONTENT_TYPES:
                if file.size > settings.MAX_UPLOAD_SIZE:
                    raise NotAcceptable({'error': 'Please keep file size under %s KB. Current file size %s KB'
                                                  % (settings.MAX_UPLOAD_SIZE, file.size)})
            else:
                raise UnsupportedMediaType(file.name)

        return attrs

    def create(self, validated_data):
        return Email.objects.create(**validated_data)
