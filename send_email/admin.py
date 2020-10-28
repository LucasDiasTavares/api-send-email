import csv
from django.http import HttpResponse
from django.contrib import admin
from .models import Email, Provider
from django_celery_results.models import TaskResult

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

try:
    ALLOW_EDITS = settings.DJANGO_CELERY_RESULTS['ALLOW_EDITS']
except (AttributeError, KeyError):
    ALLOW_EDITS = False
    pass


def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export selected as CSV"


class TaskResultAdmin(admin.ModelAdmin, ExportCsvMixin):
    date_hierarchy = 'date_done'
    list_display = ('task_id', 'task_name', 'date_done', 'status', 'worker')
    list_filter = ('status', 'date_done', 'task_name', 'worker')
    readonly_fields = ('date_created', 'date_done', 'result', 'meta')
    search_fields = ('task_name', 'task_id', 'status')
    fieldsets = (
        (None, {
            'fields': (
                'task_id',
                'task_name',
                'status',
                'worker',
                'content_type',
                'content_encoding',
            ),
            'classes': ('extrapretty', 'wide')
        }),
        (_('Parameters'), {
            'fields': (
                'task_args',
                'task_kwargs',
            ),
            'classes': ('extrapretty', 'wide')
        }),
        (_('Result'), {
            'fields': (
                'result',
                'date_created',
                'date_done',
                'traceback',
                'meta',
            ),
            'classes': ('extrapretty', 'wide')
        }),
    )
    actions = ["export_as_csv"]

    def get_readonly_fields(self, request, obj=None):
        if ALLOW_EDITS:
            return self.readonly_fields
        else:
            return list(set(
                [field.name for field in self.opts.local_fields]
            ))


admin.site.unregister(TaskResult)
admin.site.register(TaskResult, TaskResultAdmin)


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ("emailFrom", "emailTo", "subject", "created_at", "user_clicked")
    readonly_fields = ('user_clicked', 'task_id', 'emailFrom', 'emailTo', 'subject', 'created_at', 'content', 'file')
    list_filter = (('emailFrom', custom_titled_filter('Email Sender')),
                   ('created_at', custom_titled_filter('Date')))
    search_fields = ("emailFrom__icontains", "subject__icontains", "emailTo__icontains")
    actions = ["export_as_csv"]


admin.site.register(Provider)
