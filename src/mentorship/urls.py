from django.urls import path
from .views import MyCurrentMatchView, MyMatchHistoryView, MyMatchSessionsView

urlpatterns = [
    path("my-match/", MyCurrentMatchView.as_view()),
    path("my-match/sessions/", MyMatchSessionsView.as_view()),
    path("match-history/", MyMatchHistoryView.as_view()),
]
