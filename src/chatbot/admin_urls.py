from django.urls import path
from .views import AdminChatbotDocumentCreateView, AdminChatbotDocumentView

urlpatterns = [
    path("documents/", AdminChatbotDocumentCreateView.as_view()),
    path("documents/<str:document_id>/", AdminChatbotDocumentView.as_view()),
]
