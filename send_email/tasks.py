from __future__ import absolute_import, unicode_literals
from celery.decorators import task
from celery.utils.log import get_task_logger
# from .email import send_email
from email.mime.image import MIMEImage
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


logger = get_task_logger(__name__)


@task(name="send_email_task")
def send_email_task(subject, email_from, email_to, content, file=None, file_name=None, file_type=None):
    context = {
        'content': content,
    }
    email_subject = subject
    html_content = render_to_string('email_message.html', context)
    email = EmailMultiAlternatives(
        email_subject, html_content,
        email_from, [email_to, ],
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

    return email.send(fail_silently=False)
    # return send_email(subject, email, email2, content, file, file_name, file_type)
