from django.contrib import admin
from .models import Email


def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ("emailFrom", "emailTo", "subject", "created_at")
    list_filter = (('emailFrom', custom_titled_filter('Email Sender')),
                   ('created_at', custom_titled_filter('Date')))
    search_fields = ("emailFrom__icontains", "subject__icontains")

