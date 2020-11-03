from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SendEmailAPIView, SendEmailDetailAPIView, SendEmailCheckClickAPIView, pixel_gif


router = DefaultRouter()
router.register(r"", SendEmailCheckClickAPIView)

urlpatterns = [
    path("pixel/", include(router.urls), name="task-detail"),
    path("",
         SendEmailAPIView.as_view(), name="tasks"),
    path("<uuid:task_id>/",
         SendEmailDetailAPIView.as_view(), name="task-detail"),
    # Pixel
    path('lucas/', pixel_gif, name='pixel'),
]
