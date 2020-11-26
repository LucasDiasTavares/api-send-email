import os
import tempfile
import re
from django.shortcuts import redirect
from rest_framework import status, viewsets
from django_fsm import TransitionNotAllowed
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, RetrieveAPIView, get_object_or_404
from .serializers import SendEmailSerializer, SendEmailSerializerPixel, EmailClickCreateSerializer
from .tasks import send_email_task
from .models import Email, Provider, EmailClick
from requests import post
from requests.exceptions import RequestException

# Pixel
import base64
from django.http.response import HttpResponse
from django.conf import settings


# Methods
def filter_provider_exists(provider):
    qs = Provider.objects.filter(EMAIL_HOST_USER=provider)
    if qs.exists():
        return qs[0]
    return None


class SendEmailAPIView(GenericAPIView):
    serializer_class = SendEmailSerializer

    def post(self, request):
        email = request.data
        serializer = self.serializer_class(data=email)
        serializer.is_valid(raise_exception=True)
        srl = serializer.save()

        subject = request.data['subject']
        content = request.data['content']
        email_from = request.data['emailFrom']
        email_to = request.data['emailTo']

        current_email_instance = Email.objects.filter(id=srl.id)
        for email_emailclick in current_email_instance:
            email_emailclick_urls = email_emailclick.urls.all()

            if len(email_emailclick_urls) > 0:
                for single_url_from_email_instance in email_emailclick_urls:
                    str_link = str(single_url_from_email_instance.url_link)
                    # Regex pattern register
                    pattern = re.compile(str_link)
                    # Replace old url
                    srl.content = pattern.sub((r'%s/sendemail/click/%s/user_click/?link=%s' %
                                               (settings.URL_DOMAIN, single_url_from_email_instance.id, str_link)
                                               ), srl.content)
                    content = srl.content
                    srl.save()

        provider = filter_provider_exists(request.data['emailFrom'])

        if provider:
            EMAIL_PORT = provider.EMAIL_PORT
            EMAIL_HOST = provider.EMAIL_HOST
            EMAIL_HOST_PASSWORD = provider.EMAIL_HOST_PASSWORD

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
                    # with file
                    current_task = send_email_task.delay(
                        subject, email_from, email_to, content, srl.webhook, EMAIL_HOST, EMAIL_PORT,
                        EMAIL_HOST_PASSWORD, tempfn, file_name, file_type)
                    # populate my model Email.task_id with the current task id
                    srl.task_id = current_task.id
                    srl.save()
                    return Response(
                        {'taskId': current_task.id, 'from': srl.email_from, 'to': srl.email_to,
                         'status': current_task.state}, status=status.HTTP_200_OK)

            else:
                # without file
                current_task = send_email_task.delay(
                    subject, email_from, email_to, content, srl.webhook, EMAIL_HOST, EMAIL_PORT,
                    EMAIL_HOST_PASSWORD)
                # populate my model Email.task_id with the current task id
                srl.task_id = current_task.id
                srl.save()
                return Response(
                    {'taskId': current_task.id, 'from': email_from, 'to': email_to,
                     'status': current_task.state}, status=status.HTTP_200_OK)

        else:
            return Response(
                {'taskId': None, 'from': email_from, 'to': email_to,
                 'message': 'Email unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)


class SendEmailDetailAPIView(RetrieveAPIView):
    serializer_class = SendEmailSerializer
    queryset = Email.objects.all()
    lookup_field = 'task_id'

    def get_object(self):
        queryset = self.get_queryset()
        return get_object_or_404(queryset, task_id=self.kwargs["task_id"])


PIXEL_GIF_DATA = base64.b64decode(
    b"R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")


class SendEmailCheckUserOpennedAPIView(viewsets.ReadOnlyModelViewSet):
    queryset = Email.objects.all()
    serializer_class = SendEmailSerializerPixel
    lookup_field = 'task_id'

    def get_object(self):
        queryset = self.get_queryset()
        return get_object_or_404(queryset, task_id=self.kwargs["task_id"])

    @action(detail=True)
    def user_openned(self, request, task_id=None):
        email = get_object_or_404(Email, task_id=task_id)
        try:
            email.user_viwed_email()
            email.save()
            post(f'{email.url_linkEmail.webhook}/',
                 data={'tracker_id': email.url_linkEmail.task_id,
                       'type': 'Opened'})
        except TransitionNotAllowed as e:
            raise ValidationError(e)
        return HttpResponse(PIXEL_GIF_DATA, content_type='image/gif')


class EmailUserClickAPIView(viewsets.ReadOnlyModelViewSet):
    queryset = EmailClick.objects.all()
    serializer_class = EmailClickCreateSerializer
    lookup_field = 'id'

    def get_object(self):
        queryset = self.get_queryset()
        return get_object_or_404(queryset, id=self.kwargs["id"])

    @action(detail=True)
    def user_click(self, request, id=None):
        email = get_object_or_404(EmailClick, id=id)
        try:
            email.user_clicked_in_the_link()
            email.save()
            post(f'{email.url_linkEmail.webhook}/',
                 data={'tracker_id': email.url_linkEmail.task_id,
                       'link': email.url_link,
                       'type': 'Click'})
        except (TransitionNotAllowed, RequestException):
            return redirect(email.url_link)
        return redirect(email.url_link)
