from django.urls import path
from .views import (
    MonthlyPTOView,
    PTOsView,
    PTOView,
    PTOReviewView,
    ReceivedPTORequestsView,
)

urlpatterns = [
    path("", PTOsView.as_view()),
    path("monthly-view/", MonthlyPTOView.as_view()),
    path("received/", ReceivedPTORequestsView.as_view()),
    path("<str:pto_id>", PTOView.as_view()),
    path("<str:pto_id>/review", PTOReviewView.as_view()),
]
