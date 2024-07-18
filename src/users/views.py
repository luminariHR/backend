from rest_framework import viewsets
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import EmployeeSerializer, UserInviteSerializer
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
