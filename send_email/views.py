import os
import tempfile

from django_fsm import TransitionNotAllowed
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, NotAuthenticated
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView, get_object_or_404
from .serializers import SendEmailSerializer
from .tasks import send_email_task
from .models import Email


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

        if Email.objects.filter(emailFrom=email_from):
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
                    send_email_task.delay(subject, email_from, email_to, content, tempfn,
                                          file_name, file_type)
            else:
                send_email_task.delay(subject, email_from, email_to, content)

            return Response({'message': f'Email está na fila'}, status=status.HTTP_200_OK)

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
