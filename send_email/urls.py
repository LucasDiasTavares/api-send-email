from django.urls import path
from send_email.views import SendEmailAPIView, SendEmailDetailAPIView

urlpatterns = [
    path("",
         SendEmailAPIView.as_view(), name="tasks"),
    path("<int:pk>/",
         SendEmailDetailAPIView.as_view(), name="task-detail"),
]
