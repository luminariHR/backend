from django.urls import path, include
from .views import NotificationsView, ReadAllView

urlpatterns = [
    path("", NotificationsView.as_view()),
    path("read-all/", ReadAllView.as_view()),
]
