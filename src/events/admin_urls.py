from django.urls import path
from .views import AdminEventCreateView, AdminEventsView

urlpatterns = [
    path("", AdminEventCreateView.as_view()),
    path("<int:event_id>", AdminEventsView.as_view()),
]
