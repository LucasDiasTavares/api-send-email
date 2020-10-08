from __future__ import absolute_import, unicode_literals
from celery.decorators import task
from celery.utils.log import get_task_logger
from send_email.email import send_email
from django.core.management import call_command
import sys


logger = get_task_logger(__name__)


@task(name="send_email_task")
def send_email_task(name, email, email2, content, file=None, file_name=None, file_type=None):
    sys.stdout = open('db.json', 'w')
    call_command('dumpdata', 'send_email')
    return send_email(name, email, email2, content, file, file_name, file_type)
