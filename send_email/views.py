import os
import tempfile
from rest_framework import generics, status
from rest_framework.response import Response

from send_email.serializers import SendEmailSerializer
from send_email.tasks import send_email_task


class SendEmailAPIView(generics.GenericAPIView):
    serializer_class = SendEmailSerializer

    def post(self, request):

        name = request.data['name']
        content = request.data['content']
        email_from = request.data['emailFrom']
        email_to = request.data['emailTo']

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
                send_email_task.delay(name, email_from, email_to, content, tempfn, file_name, file_type)

        else:
            send_email_task.delay(name, email_from, email_to, content)

        return Response({'message': 'Email successfully sended'}, status=status.HTTP_200_OK)
