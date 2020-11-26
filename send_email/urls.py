from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (SendEmailAPIView, SendEmailDetailAPIView, SendEmailCheckUserOpennedAPIView,
                    EmailUserClickAPIView)


router = DefaultRouter()
router.register(r"", SendEmailCheckUserOpennedAPIView)

router2 = DefaultRouter()
router2.register(r"", EmailUserClickAPIView)


urlpatterns = [
    # Img pixel at end of email, when user open, change to TRUE
    path("pixel/", include(router.urls), name="task-detail"),

    # Email User Click List/Detail using id if in detail view you can active action "user click" to change
    # the value "user_clicked_link": "False", to True /sendemail/click/{id}/user_click/
    path("click/", include(router2.urls), name="click-detail"),

    # Create a new email instance and send it
    path("",
         SendEmailAPIView.as_view(), name="tasks"),

    # Get any task by uuid
    path("<uuid:task_id>/",
         SendEmailDetailAPIView.as_view(), name="task-detail"),
]
