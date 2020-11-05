from __future__ import absolute_import, unicode_literals
from celery.task import task
from celery import Task, current_task
from celery.result import AsyncResult
from celery.utils.log import get_task_logger
from email.mime.image import MIMEImage
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, get_connection
import requests
import random


logger = get_task_logger(__name__)


class CallbackTask(Task):
    def on_success(self, retval, task_id, args, kwargs):
        res = AsyncResult(task_id)
        # return requests.post('https://anotherapi.com',
        #                      data={'id': res.id, 'state': res.state, 'from': list(args)[1], 'to': list(args)[2]})

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        res = AsyncResult(task_id)
        # return requests.post('https://anotherapi.com',
        #                      data={'id': res.id, 'state': res.state, 'from': list(args)[1], 'to': list(args)[2]})


@task(bind=True, name="send_email_task", autoretry_for=(ConnectionRefusedError,), max_retries=10)
def send_email_task(self, subject, email_from, email_to, content,
                    EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_PASSWORD,
                    file=None, file_name=None, file_type=None):

    try:
        task_link = f'https://localhost:8000/sendemail/pixel/{current_task.request.id}/user_click/'
        task_id = current_task.request.id

        context = {
            'content': content,
            'task_link': task_link,
            'task_id': task_id
        }

        html_content = render_to_string('email_message.html', context)

        with get_connection(
                host=EMAIL_HOST,
                port=EMAIL_PORT,
                username=email_from,
                password=EMAIL_HOST_PASSWORD,
                use_tls=True) as connection:

            email = EmailMultiAlternatives(
                subject, html_content,
                email_from, [email_to, ],
                connection=connection
            )

            if file:
                if 'image' in file_type:
                    with open(file, 'rb') as f:
                        image = MIMEImage(f.read())
                        image.add_header('Content-Disposition', 'attachment', filename=file_name)
                        email.attach(image)
                else:
                    with open(file, 'rb') as f:
                        email.attach(file_name, f.read(), file_type)

            email.attach_alternative(html_content, "text/html")

            email.send(fail_silently=False)
    except ConnectionRefusedError as exc:
        self.retry(exc=exc, countdown=int(random.uniform(2, 4) ** random.uniform(2, 3)))
