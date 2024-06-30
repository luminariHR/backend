from .models import Department, DepartmentUser
from .serializers import DepartmentSerializer, DepartmentListSerializer
from django.db.models import Prefetch
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


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
        active_members = DepartmentUser.objects.filter(is_current=True)
        departments_with_active_members = Department.objects.filter(
            id=dept_id
        ).prefetch_related(Prefetch("members", queryset=active_members))
        serializer = DepartmentSerializer(departments_with_active_members, many=True)
        return Response(serializer.data)
