from __future__ import absolute_import, unicode_literals
import random
from celery.task import task
from celery import Task, current_task
from celery.result import AsyncResult
from celery.utils.log import get_task_logger
from email.mime.image import MIMEImage
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, get_connection
from requests import post
from requests.exceptions import RequestException

logger = get_task_logger(__name__)
'''
Here print() or import pdb; pdb.pdb.set_trace(); don't works,
so we can debug with logger.info if you run celery with
celery worker --app=core --pool=solo --loglevel=INFO in Windows
or celery -A core worker --loglevel=info in Linux
e.g. logger.info(f'{res} - debugging asyncResult')
 '''


class CallbackTask(Task):
    def on_success(self, retval, task_id, args, kwargs):
        res = AsyncResult(task_id)
        try:
            return post(f'{list(args)[4]}/',
                        data={'tracker_id': res.id,
                              'type': 'Send',
                              'email_from': list(args)[1],
                              'email_to': list(args)[2]})

        except RequestException:
            return None

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        res = AsyncResult(task_id)
        try:
            return post(f'{list(args)[4]}/',
                        data={'tracker_id': res.id,
                              'type': 'Failure',
                              'error': exc.args,
                              'email_from': list(args)[1],
                              'email_to': list(args)[2]})

        except RequestException:
            return None


@task(base=CallbackTask, bind=True, name="send_email_task",
      autoretry_for=(ConnectionRefusedError, ConnectionError,), max_retries=5)
def send_email_task(self, subject, email_from, email_to, content, webhook, EMAIL_HOST, EMAIL_PORT,
                    EMAIL_HOST_PASSWORD, file=None, file_name=None, file_type=None):
    # Do not remove webhook we use in def on_success and def on_failure'

    try:
        task_id = current_task.request.id

        task_link_user_openned_email = f'{settings.URL_DOMAIN}/sendemail/pixel/{task_id}/user_click/'

        context = {
            'content': content,
            'task_link_user_openned_email': task_link_user_openned_email,
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
                    # Other kind of attach: .txt, .doc, etc.
                    with open(file, 'rb') as f:
                        email.attach(file_name, f.read(), file_type)

            email.attach_alternative(html_content, "text/html")

            email.send(fail_silently=False)
    except (ConnectionRefusedError, ConnectionError) as exc:
        self.retry(exc=exc, countdown=int(random.uniform(2, 4) ** random.uniform(2, 3)))
