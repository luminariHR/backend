from django.urls import path
from .views import (
    MentorsView,
    MentorView,
    MenteesView,
    MenteeView,
    AvailableEmployeesView,
    MatchesView,
    MyCurrentMatchView,
    MyMatchHistoryView,
    MentorRecommendationView,
    SessionsView,
)

urlpatterns = [
    path("mentors/", MentorsView.as_view()),
    path("mentees/", MenteesView.as_view()),
    path("mentors/<int:id>/", MentorView.as_view()),
    path("mentees/<int:id>/", MenteeView.as_view()),
    path(
        "available/",
        AvailableEmployeesView.as_view(),
    ),
    path("matches/", MatchesView.as_view()),
    path("matches/<int:match_id>/sessions/", SessionsView.as_view()),
    path(
        "recommendations/",
        MentorRecommendationView.as_view(),
    ),
]
