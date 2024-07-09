from django.urls import path
from .views import AdminAppointmentView

urlpatterns = [
    path("", AdminAppointmentView.as_view()),
]
