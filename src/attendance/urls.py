from django.urls import path
from .views import AttendanceView, ClockInView, ClockOutView, AttendanceUpdateView

urlpatterns = [
    path("", AttendanceView.as_view()),
    path("clock-in", ClockInView.as_view()),
    path("clock-out", ClockOutView.as_view()),
    path("<int:attendance_id>", AttendanceUpdateView.as_view()),
]
