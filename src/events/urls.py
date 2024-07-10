from django.urls import path
from .views import EventsView, EventView

urlpatterns = [
    path("", EventsView.as_view()),
    path("<int:event_id>", EventView.as_view()),
]
