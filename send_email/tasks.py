from __future__ import absolute_import, unicode_literals
from celery import current_task
from celery.decorators import task
from celery.utils.log import get_task_logger
from email.mime.image import MIMEImage
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, get_connection


logger = get_task_logger(__name__)


@task(name="send_email_task")
def send_email_task(subject, email_from, email_to, content,
                    EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_PASSWORD,
                    file=None, file_name=None, file_type=None):
    context = {
        'content': content,
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

        return logger.info(f'=> email sended {email_from} - {email_to} <=')
        # return logger.info(current_task)
