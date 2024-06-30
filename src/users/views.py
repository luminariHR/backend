from rest_framework import viewsets
from rest_framework.exceptions import MethodNotAllowed
from .serializers import EmployeeSerializer
from .models import Employee
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsHRAdmin, IsHRAdminOrSelf


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.filter(is_superuser=False)
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        return Employee.objects.filter(is_superuser=False)

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsAuthenticated]
        elif self.action == "create":
            permission_classes = [IsHRAdmin]
        elif self.action in ["update", "partial_update"]:
            permission_classes = [IsHRAdminOrSelf]
        elif self.action == "destroy":
            raise MethodNotAllowed("DELETE")
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
