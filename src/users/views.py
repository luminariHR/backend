from rest_framework import viewsets
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import EmployeeSerializer, UserInviteSerializer
from .models import Employee
from core.permissions import IsHRAdmin, IsHRAdminOrSelf
from core.pagination import DefaultLimitOffsetPagination
from django.db.models import Prefetch
from departments.models import Department


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    pagination_class = DefaultLimitOffsetPagination

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            queryset = Employee.objects.prefetch_related(
                Prefetch(
                    "department",
                    queryset=Department.objects.prefetch_related("members"),
                )
            ).filter(is_superuser=False)
        else:
            queryset = Employee.objects.filter(is_superuser=False)
        return queryset

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
        employee = Employee.objects.prefetch_related(
            Prefetch(
                "department", queryset=Department.objects.prefetch_related("members")
            )
        ).get(id=user_id)
        serializer = EmployeeSerializer(employee, context=context)
        return Response(serializer.data, status=200)


class UserInviteView(APIView):

    permission_classes = [IsHRAdmin]

    def post(self, request, version):
        """
        email
        employee_id
        gender
        employment_status
        job_title
        phone_number
        start_date
        """
        context = {"request": request}
        email_address = request.data["email"]
        employee_id = request.data["employee_id"]
        if Employee.objects.filter(email=email_address).exists():
            return Response({"message": "이미 존재하는 이메일입니다."}, status=400)
        if Employee.objects.filter(employee_id=employee_id).exists():
            return Response({"message": "이미 존재하는 사번입니다."}, status=400)
        serializer = UserInviteSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "성공적으로 초대되었습니다.", "data": serializer.data}
            )
        return Response(serializer.errors, status=400)
