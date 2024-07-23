from django.urls import path
from .views import (
    MentorCreateView,
    MenteeCreateView,
    MenteeListView,
    MentorListView,
    AvailableEmployeesView,
    MatchCreateView,
    MatchListView,
    MatchUserView,
    MatchDeleteView,
    MentorRecommendationView,
)

urlpatterns = [
    path("mentorship/mentors/", MentorCreateView.as_view(), name="mentor-create"),
    path("mentorship/mentees/", MenteeCreateView.as_view(), name="mentee-create"),
    path("mentorship/mentees/list/", MenteeListView.as_view(), name="mentee-list"),
    path("mentorship/mentors/list/", MentorListView.as_view(), name="mentor-list"),
    path(
        "mentorship/available/",
        AvailableEmployeesView.as_view(),
        name="available-employees",
    ),
    path("mentorship/matches/", MatchCreateView.as_view(), name="match-create"),
    path("mentorship/matches/list/", MatchListView.as_view(), name="match-list"),
    path("mentorship/matches/user/", MatchUserView.as_view(), name="match-user"),
    path(
        "mentorship/matches/<int:id>/", MatchDeleteView.as_view(), name="match-delete"
    ),
    path(
        "mentorship/mentees/recommendations/",
        MentorRecommendationView.as_view(),
        name="mentor-recommendations",
    ),
]
