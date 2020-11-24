from datetime import timedelta
from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition


class Email(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    task_id = models.CharField(max_length=256, null=True, blank=True)
    subject = models.CharField(max_length=256)
    content = models.CharField(max_length=65535)
    emailFrom = models.EmailField(max_length=256)
    emailTo = models.EmailField(max_length=256)
    file = models.FileField(null=True, blank=True)
    user_openned_email = FSMField(default='False')

    @transition(field=user_openned_email, source='False', target='True')
    def user_viwed_email(self):
        pass

    def was_sended_recently(self):
        now = timezone.now()
        return now - timedelta(days=1) <= self.created_at <= now

    class Meta:
        ordering = ("-created_at", )

    def __str__(self):
        return f'{self.id} - {self.task_id}'


class EmailClick(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    url_link = models.CharField(max_length=256, default='', null=True, blank=True)
    url_linkEmail = models.ForeignKey(Email, blank=True, null=True, related_name="urls", on_delete=models.CASCADE)
    user_clicked_link = FSMField(default='False')

    @transition(field=user_clicked_link, source='False', target='True')
    def user_clicked_in_the_link(self):
        pass

    class Meta:
        ordering = ("-created_at", )

    def __str__(self):
        return str(self.url_linkEmail) if self.url_linkEmail else ''


class Provider(models.Model):
    EMAIL_HOST = models.CharField(max_length=256)
    EMAIL_PORT = models.PositiveSmallIntegerField()
    EMAIL_HOST_USER = models.CharField(max_length=256)
    EMAIL_HOST_PASSWORD = models.CharField(max_length=256)

    def __str__(self):
        return self.EMAIL_HOST_USER
