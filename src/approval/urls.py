from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SentApprovalViewSet,
    ReviewApprovalViewSet,
    AgendaReviewRequestCreateView,
    AgendaReviewView,
    SentReviewRequestView,
    ReceivedReviewRequestView,
    ReferencedReviewRequestView,
)

# router = DefaultRouter()
# router.register(r"sent", SentApprovalViewSet, basename="request-approvals")
# router.register(r"received", ReviewApprovalViewSet, basename="approve-approvals")

urlpatterns = [
    # path("", include(router.urls)),
    path("documents/", AgendaReviewRequestCreateView.as_view()),
    path("documents/<int:agenda_id>/", AgendaReviewView.as_view()),
    path("documents/sent/", SentReviewRequestView.as_view()),
    path("documents/received/", ReceivedReviewRequestView.as_view()),
    path("documents/referenced/", ReferencedReviewRequestView.as_view()),
]
