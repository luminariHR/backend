from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from core.permissions import IsTaskAssignee
from .models import Task
from .serializers import TaskSerializer, BoardSerializer


# 일반 유저 View
class BoardView(APIView):
    @permission_classes([IsAuthenticated])
    def get(self, request, version):
        # 본인 리스트만 조회 가능
        context = {"request": request}
        today = timezone.now().date()
        tasks = Task.objects.filter(
            Q(is_deleted=False)
            & Q(assignee_id=request.user.id)
            & ~(Q(status="completed") & Q(end_date__lt=today))
        )
        serializer = BoardSerializer(tasks, context=context)
        return Response(serializer.data)


class TaskCreateView(APIView):
    @permission_classes([IsAuthenticated])
    def post(self, request, version):
        context = {"request": request}
        serializer = TaskSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "성공적으로 생성되었습니다.", "data": serializer.data}
            )
        return Response(serializer.errors, status=400)


class TaskDetailView(APIView):

    permission_classes = [IsTaskAssignee]

    def get_task(self, item_id):
        task = get_object_or_404(Task, id=item_id)
        self.check_object_permissions(self.request, task)
        return task

    def get(self, request, version, item_id):
        item = self.get_task(item_id)
        serializer = TaskSerializer(item)
        return Response(serializer.data)

    def patch(self, request, version, item_id):
        context = {"request": request}
        item = self.get_task(item_id)
        serializer = TaskSerializer(
            item, data=request.data, partial=True, context=context
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "성공적으로 업데이트 됐습니다.", "data": serializer.data}
            )
        return Response({"errors": serializer.errors}, status=400)

    def delete(self, request, version, item_id):
        context = {"request": request}
        # 논리적 삭제: is_deleted
        item = self.get_task(item_id)
        item.is_deleted = True
        serializer = TaskSerializer(
            item, data={"is_deleted": True}, partial=True, context=context
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "성공적으로 삭제되었습니다."})
        return Response(serializer.errors, status=400)
