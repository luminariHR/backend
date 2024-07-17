from rest_framework import viewsets
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import EmployeeSerializer
from .models import Employee
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


class MyProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, version):
        context = {"request": request}
        # 본인 프로필
        user_id = request.user.id
        employee = Employee.objects.get(id=user_id)
        serializer = EmployeeSerializer(employee, context=context)
        return Response(serializer.data, status=200)
