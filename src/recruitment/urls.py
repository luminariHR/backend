from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r"postings", JobPostingViewSet)
router.register(r"questions", EssayQuestionViewSet)
# router.register(r"answers", EssayAnswerViewSet)
router.register(r"summaries", SummaryViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "postings/<int:posting_id>/applicants/",
        JobPostingApplicantsView.as_view(),
        name="posting_applicants",
    ),
    path(
        "postings/<int:posting_id>/applicants/<str:applicant_email>/",
        ApplicantEssayAnswersView.as_view(),
        name="applicant_essays",
    ),
    path(
        "answers/<int:posting_id>/",
        AnswerView.as_view(),
        name="posting_answer",
    ),
]
