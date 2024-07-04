from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import ChatbotDocumentList, ChatbotDocumentDetail

urlpatterns = [
    path(
        "messages/", views.MessageListCreateView.as_view(), name="message-list-create"
    ),
    path("documents/", ChatbotDocumentList.as_view(), name="document-list"),
    path(
        "documents/<int:pk>/", ChatbotDocumentDetail.as_view(), name="document-destroy"
    ),
]
