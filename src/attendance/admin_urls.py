from django.urls import path
from .views import AdminAttendanceView, AdminAttendanceUpdateView

urlpatterns = [
    path("users/<int:user_id>", AdminAttendanceView.as_view()),
    path("<int:attendance_id>", AdminAttendanceUpdateView.as_view()),
]
