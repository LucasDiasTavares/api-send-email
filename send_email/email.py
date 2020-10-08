from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


def send_email(name, email_from, email_to, content, file, file_name, file_type):
    context = {
        'name': name,
        'emailFrom': email_from,
        'content': content,
        'emailTo': email_to,
    }

    email_subject = email_to
    html_content = render_to_string('email_message.html', context)

    email = EmailMultiAlternatives(
        email_subject, html_content,
        email_from, [email_to, ],
    )
    if file:
        f = open(file, 'r')
        email.attach(file_name, f.read(), file_type)

    email.attach_alternative(html_content, "text/html")

    return email.send(fail_silently=False)
