import os
import tempfile

from django_fsm import TransitionNotAllowed
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView, get_object_or_404
from .serializers import SendEmailSerializer
from .tasks import send_email_task
from .models import Email, Provider


# Methods
def filter_email_exists(email):
    qs = Provider.objects.filter(EMAIL_HOST_USER=email)
    if qs.exists():
        return qs[0]
    return None


class SendEmailAPIView(GenericAPIView):
    serializer_class = SendEmailSerializer

    def post(self, request):
        email = request.data
        serializer = self.serializer_class(data=email)
        serializer.is_valid(raise_exception=True)

        subject = request.data['subject']
        content = request.data['content']
        email_from = request.data['emailFrom']
        email_to = request.data['emailTo']

        email = filter_email_exists(request.data['emailFrom'])

        if email:
            EMAIL_PORT = email.EMAIL_PORT
            EMAIL_HOST = email.EMAIL_HOST
            EMAIL_HOST_PASSWORD = email.EMAIL_HOST_PASSWORD

            if request.FILES:
                attachment = request.FILES['file']
                file_name = attachment.name
                file_type = attachment.content_type

                tempf, tempfn = tempfile.mkstemp()
                try:
                    for chunk in attachment.chunks():
                        os.write(tempf, chunk)
                except:
                    raise Response({'error': "Problem with the input file %s" % file_name},
                                   status=status.HTTP_404_NOT_FOUND)
                finally:
                    send_email_task.delay(subject, email_from, email_to, content,
                                          EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_PASSWORD,
                                          tempfn, file_name, file_type)
            else:
                send_email_task.delay(
                    subject, email_from, email_to, content, EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_PASSWORD)

            return Response({'message': f'Email on queue {email_from} - {email_to}'}, status=status.HTTP_200_OK)

        else:
            return Response({'error': f'Email unauthorized {email_from}'}, status=status.HTTP_401_UNAUTHORIZED)


# UpdateAPIView
class SendEmailDetailAPIView(RetrieveUpdateAPIView):
    serializer_class = SendEmailSerializer
    queryset = Email.objects.all()

    @action(detail=True)
    def new(self, request, pk=None):
        email = get_object_or_404
        try:
            email.new()
            email.save()
        except TransitionNotAllowed as e:
            raise ValidationError(e)
        return Response({'status': 'works'})
