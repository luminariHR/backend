from .models import Department
from .serializers import (
    DepartmentSerializer,
    DepartmentListSerializer,
    AdminDepartmentSerializer,
)
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from core.permissions import IsHRAdmin


class DepartmentListView(APIView):
    @permission_classes([IsAuthenticated])
    def get(self, request, version):
        include_deleted = request.GET.get("include_deleted", False)
        if include_deleted == "true":
            include_deleted = True
        else:
            include_deleted = False
        departments = Department.objects.filter(
            Q(is_deleted=False) | Q(is_deleted=include_deleted)
        )
        serializer = DepartmentListSerializer(departments, many=True)
        return Response(serializer.data)


class DepartmentView(APIView):
    @permission_classes([IsAuthenticated])
    def get(self, request, version, dept_id):
        context = {"request": request}
        departments = Department.objects.filter(id=dept_id)
        serializer = DepartmentSerializer(departments, many=True, context=context)
        return Response(serializer.data)


# HR 관리자 View
class AdminDepartmentCreateView(APIView):

    permission_classes = [IsHRAdmin]

    def post(self, request, version):
        context = {"request": request}
        serializer = AdminDepartmentSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "성공적으로 부서가 생성되었습니다.",
                    "data": serializer.data,
                }
            )
        return Response(serializer.errors, status=400)


class AdminDepartmentUpdateView(APIView):

    permission_classes = [IsHRAdmin]

    def get_department(self, department_id):
        department = get_object_or_404(Department, id=department_id)
        self.check_object_permissions(self.request, department)
        return department

    def patch(self, request, version, department_id):
        context = {"request": request}
        department = self.get_department(department_id)
        serializer = AdminDepartmentSerializer(
            department, data=request.data, partial=True, context=context
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "부서가 성공적으로 업데이트 됐습니다.",
                    "data": serializer.data,
                }
            )
        return Response({"errors": serializer.errors}, status=400)

    def delete(self, request, version, department_id):
        context = {"request": request}
        department = self.get_department(department_id)
        serializer = AdminDepartmentSerializer(
            department, data={"is_deleted": True}, partial=True, context=context
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "부서가 성공적으로 삭제 됐습니다.",
                    "data": serializer.data,
                }
            )
        return Response({"errors": serializer.errors}, status=400)
