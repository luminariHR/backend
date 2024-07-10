from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SentApprovalViewSet, ReviewApprovalViewSet

router = DefaultRouter()
router.register(r"sent", SentApprovalViewSet, basename="request-approvals")
router.register(r"received", ReviewApprovalViewSet, basename="approve-approvals")

urlpatterns = [
    path("", include(router.urls)),
]
