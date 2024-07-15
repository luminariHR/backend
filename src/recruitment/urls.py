from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobPostingViewSet, EssayQuestionViewSet, EssayAnswerViewSet

router = DefaultRouter()
router.register(r"postings", JobPostingViewSet)
router.register(r"questions", EssayQuestionViewSet)
router.register(r"answers", EssayAnswerViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
