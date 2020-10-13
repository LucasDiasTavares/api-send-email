from __future__ import absolute_import, unicode_literals
from celery.decorators import task
from celery.utils.log import get_task_logger
from .email import send_email


logger = get_task_logger(__name__)


@task(name="send_email_task")
def send_email_task(subject, email, email2, content, file=None, file_name=None, file_type=None):
    return send_email(subject, email, email2, content, file, file_name, file_type)
