import os
import tempfile

from rest_framework import status, viewsets
from django_fsm import TransitionNotAllowed
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, RetrieveAPIView, get_object_or_404
from .serializers import SendEmailSerializer, SendEmailSerializerClick
from .tasks import send_email_task
from .models import Email, Provider

# Pixel
import base64
from django.http.response import HttpResponse


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

                # django write/read InMemoryUploadedFile
                tempf, tempfn = tempfile.mkstemp()
                try:
                    for chunk in attachment.chunks():
                        os.write(tempf, chunk)
                except:
                    raise Response({'error': "Problem with the input file %s" % file_name},
                                   status=status.HTTP_404_NOT_FOUND)
                finally:
                    t = send_email_task.delay(subject, email_from, email_to, content,
                                          EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_PASSWORD,
                                          tempfn, file_name, file_type)
                    # populate my model Email.task_id with the current task id
                    serializer.validated_data['task_id'] = t.id
                    serializer.save()
                    return Response(
                        {'taskId': t.id, 'from': email_from, 'to': email_to,
                         'status': t.state}, status=status.HTTP_200_OK)

            else:
                t = send_email_task.delay(
                    subject, email_from, email_to, content, EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_PASSWORD)
                # populate my model Email.task_id with the current task id
                serializer.validated_data['task_id'] = t.id
                serializer.save()
                return Response(
                    {'taskId': t.id, 'from': email_from, 'to': email_to,
                     'status': t.state}, status=status.HTTP_200_OK)

        else:
            return Response(
                {'taskId': None, 'from': email_from, 'to': email_to,
                 'message': 'Email from unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)


class SendEmailDetailAPIView(RetrieveAPIView):
    serializer_class = SendEmailSerializer
    queryset = Email.objects.all()
    lookup_field = 'task_id'

    def get_object(self):
        queryset = self.get_queryset()
        return get_object_or_404(queryset, task_id=self.kwargs["task_id"])


# Testing
class SendEmailCheckClickAPIView(viewsets.ReadOnlyModelViewSet):
    queryset = Email.objects.all()
    serializer_class = SendEmailSerializerClick
    lookup_field = 'task_id'

    def get_object(self):
        queryset = self.get_queryset()
        return get_object_or_404(queryset, task_id=self.kwargs["task_id"])

    @action(detail=True)
    def user_click(self, request, task_id=None):
        email = get_object_or_404(Email, task_id=task_id)
        try:
            email.user_clicked_in_the_link()
            email.save()
        except TransitionNotAllowed as e:
            raise ValidationError(e)
        # return HttpResponse(PIXEL_GIF_DATA, content_type='image/gif')
        return Response({'status': email.user_clicked})


PIXEL_GIF_DATA = base64.b64decode(
    b"R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")


def pixel_gif(request):
    return HttpResponse(PIXEL_GIF_DATA, content_type='image/gif')
