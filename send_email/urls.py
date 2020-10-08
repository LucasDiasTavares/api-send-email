from django.urls import path
from send_email.views import SendEmailAPIView


urlpatterns = [
    path("",
         SendEmailAPIView.as_view(), name="tasks"),
]
