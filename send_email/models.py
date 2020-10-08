from django.db import models


class Email(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=256)
    content = models.CharField(max_length=256)
    emailFrom = models.EmailField(max_length=256)
    emailTo = models.EmailField(max_length=256)
    file = models.FileField(null=True, blank=True)

    def __str__(self):
        return self.content
