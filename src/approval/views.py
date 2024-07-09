from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Approval
from .serializers import ApprovalSerializer


class RequestApprovalViewSet(viewsets.ModelViewSet):
    queryset = Approval.objects.all()
    serializer_class = ApprovalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Approval.objects.filter(requester=user)

    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)


class ApproveApprovalViewSet(viewsets.ModelViewSet):
    queryset = Approval.objects.all()
    serializer_class = ApprovalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Approval.objects.filter(approver=user)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        status_update = request.data.get("status")

        if status_update not in ["approved", "rejected", "pending"]:
            return Response(
                {"detail": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST
            )

        instance.status = status_update
        instance.save()
        print(f"Updated status: {instance.status}")
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# Create your views here.
