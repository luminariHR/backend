from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RequestApprovalViewSet, ApproveApprovalViewSet

router = DefaultRouter()
router.register(
    r"request-approvals", RequestApprovalViewSet, basename="request-approvals"
)
router.register(
    r"approve-approvals", ApproveApprovalViewSet, basename="approve-approvals"
)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "approve-approvals/<int:pk>/approve/",
        ApproveApprovalViewSet.as_view({"post": "approve"}),
        name="approve-approval",
    ),
    path(
        "approve-approvals/<int:pk>/reject/",
        ApproveApprovalViewSet.as_view({"post": "reject"}),
        name="reject-approval",
    ),
]
