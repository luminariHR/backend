from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet, ChatbotDocumentListView, ChatbotDocumentView

router = DefaultRouter()
router.register(r"messages", MessageViewSet)

urlpatterns = [
    path("documents/", ChatbotDocumentListView.as_view()),
    path("documents/<str:document_id>/", ChatbotDocumentView.as_view()),
    path("", include(router.urls)),
]
