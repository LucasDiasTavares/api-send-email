from email.mime.image import MIMEImage
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


def send_email(subject, email_from, email_to, content, file_path, file_name, file_type):
    context = {
        'content': content,
    }
    email_subject = subject
    html_content = render_to_string('email_message.html', context)

    email = EmailMultiAlternatives(
        email_subject, html_content,
        email_from, [email_to, ],
    )

    if file_path and 'image' in file_type:
        with open(file_path, 'rb') as f:
            image = MIMEImage(f.read())
            image.add_header('Content-Disposition', 'attachment', filename=file_name)
            email.attach(image)
    else:
        with open(file_path, 'rb') as f:
            email.attach(file_name, f.read(), file_type)

    email.attach_alternative(html_content, "text/html")

    return email.send(fail_silently=False)
