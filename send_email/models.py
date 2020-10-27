from datetime import timedelta
from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition


class Email(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    subject = models.CharField(max_length=256)
    content = models.CharField(max_length=65535)
    emailFrom = models.EmailField(max_length=256)
    emailTo = models.EmailField(max_length=256)
    file = models.FileField(null=True, blank=True)
    # status = FSMField(default="old")

    def was_sended_recently(self):
        now = timezone.now()
        return now - timedelta(days=1) <= self.created_at <= now

    class Meta:
        ordering = ("created_at", )

    def __str__(self):
        return self.subject

    # @transition(field=status, source='old', target='new')
    # def new(self):
    #     pass


class Provider(models.Model):
    EMAIL_HOST = models.CharField(max_length=256)
    EMAIL_PORT = models.PositiveSmallIntegerField()
    EMAIL_HOST_USER = models.CharField(max_length=256)
    EMAIL_HOST_PASSWORD = models.CharField(max_length=256)

    def __str__(self):
        return self.EMAIL_HOST_USER
