from django.conf import settings
from rest_framework.exceptions import UnsupportedMediaType, NotAcceptable
from rest_framework import serializers
from .models import Email, EmailClick
import re


class EmailClickCreateSerializer(serializers.ModelSerializer):
    email_click_task_id = serializers.SerializerMethodField()

    class Meta:
        model = EmailClick
        fields = ('id', 'created_at', 'url_link', 'url_linkEmail', 'user_clicked_link', 'email_click_task_id')

    def get_email_click_task_id(self, instance):
        return instance.url_linkEmail.task_id


class EmailClickSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailClick
        fields = '__all__'


class SendEmailSerializer(serializers.ModelSerializer):
    subject = serializers.CharField(max_length=256)
    content = serializers.CharField(max_length=65535)
    emailFrom = serializers.EmailField(max_length=256)
    emailTo = serializers.EmailField(max_length=256)
    urls = EmailClickSerializer(many=True, allow_null=True, required=False)
    webhook = serializers.EmailField(allow_null=True, allow_blank=True, required=False)

    class Meta:
        model = Email
        fields = ('id', 'task_id', 'created_at', 'user_openned_email', 'subject',  'content', 'emailFrom', 'emailTo',
                  'file', 'webhook', 'urls')

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
        validated_data.pop('urls')
        email = Email.objects.create(**validated_data)

        pattern = re.compile(r'(href=[\'\"]?)([^\'\" >]+)')
        links_inside_content = re.findall(pattern, email.content)

        for link in links_inside_content:
            EmailClick.objects.create(url_linkEmail=email, url_link=link[1])
        return email

    def update(self, instance, validated_data):
        email_urls_data = validated_data.pop('urls')
        email_urls = (instance.urls).all()
        email_urls = list(email_urls)
        instance.task_id = validated_data.get('task_id', instance.task_id)
        instance.content = validated_data.get('content', instance.content)
        instance.save()

        for album_data in email_urls_data:
            url = email_urls.pop(0)
            url.name = album_data.get('url_link', url.url_link)
            url.save()

        return instance


class SendEmailSerializerPixel(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = '__all__'
