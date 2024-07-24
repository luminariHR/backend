from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Event
from .serializers import EventSerializer
from core.permissions import IsHRAdmin


# 일반 회원 View
class EventsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, version):
        context = {"request": request}
        start_date = request.GET.get("start_date", None)
        end_date = request.GET.get("end_date", None)
        if start_date is None or end_date is None:
            return Response(
                {"message": "시작일과 종료일은 필수 파라미터입니다."}, status=400
            )
        if end_date < start_date:
            return Response(
                {"message": "종료일이 시작일보다 빠를 수 없습니다."}, status=400
            )
        attendance = Event.objects.filter(
            Q(start_date__gte=start_date) & Q(start_date__lte=end_date)
        )
        serializer = EventSerializer(attendance, context=context, many=True)
        return Response(serializer.data, 200)


class EventView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, version, event_id: str):
        context = {"request": request}
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response(
                {"message": "존재하지 않는 일정입니다."},
                status=404,
            )
        serializer = EventSerializer(event, context=context)
        return Response(serializer.data)


# HR 관리자 View
class AdminEventCreateView(APIView):

    permission_classes = [IsHRAdmin]

    def post(self, request, version):
        context = {"request": request}
        start_date = request.data.get("start_date", None)
        end_date = request.data.get("end_date", None)
        if start_date is None or end_date is None:
            return Response(
                {"message": "시작일과 종료일은 필수 파라미터입니다."}, status=400
            )
        serializer = EventSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "성공적으로 일정이 생성되었습니다.",
                    "data": serializer.data,
                }
            )
        errors = []
        for e in serializer.errors.values():
            errors += e
        return Response({"errors": errors}, status=400)


class AdminEventsView(APIView):

    permission_classes = [IsHRAdmin]

    def patch(self, request, version, event_id: str):
        context = {"request": request}
        try:
            event = Event.objects.get(id=event_id)
            self.check_object_permissions(self.request, event)
        except Event.DoesNotExist:
            return Response(
                {"message": "존재하지 않는 일정입니다."},
                status=404,
            )
        serializer = EventSerializer(
            event, data=request.data, partial=True, context=context
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "성공적으로 수정됐습니다.", "data": serializer.data}
            )
        return Response({"errors": serializer.errors}, status=400)

    def delete(self, request, version, event_id: str):
        context = {"request": request}
        try:
            event = Event.objects.get(id=event_id)
            self.check_object_permissions(self.request, event)
        except Event.DoesNotExist:
            return Response(
                {"message": "존재하지 않는 일정입니다."},
                status=404,
            )
        serializer = EventSerializer(
            event, data=request.data, partial=True, context=context
        )
        serializer.delete(event)
        return Response({"message": "성공적으로 일정이 삭제됐습니다."}, status=200)
