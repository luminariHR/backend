from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from .models import Attendance
from .serializers import AttendanceSerializer, AdminAttendanceSerializer
from core.permissions import IsSelfAttendance, IsHRAdmin


# 일반 회원 View
class AttendanceView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, version):
        context = {"request": request}
        # 'start_date', 'end_date' 없으면 오늘로 설정
        today = timezone.now().date()
        start_date = request.GET.get("start_date", today)
        end_date = request.GET.get("end_date", today)
        attendance = Attendance.objects.filter(
            Q(date__gte=start_date)
            & Q(date__lte=end_date)
            & Q(employee_id=request.user.id)
        )
        serializer = AttendanceSerializer(attendance, context=context, many=True)
        response_data = {
            "start_date": start_date,
            "end_date": end_date,
            "total_hours": 0,
            "data": serializer.data,
        }
        for att in serializer.data:
            if att["hours_worked"]:
                response_data["total_hours"] += att["hours_worked"]
        return Response(response_data)


class ClockInView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, version):
        context = {"request": request}
        today = timezone.now()
        data = {"clock_in": today}
        if "clock_in_note" in request.data:
            data["clock_in_note"] = request.data.get("clock_in_note")
        serializer = AttendanceSerializer(data=data, context=context)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(
                    {
                        "message": "정상적으로 출근이 처리됐습니다.",
                        "data": serializer.data,
                    }
                )
            except IntegrityError:
                return Response(
                    {
                        "message": "이미 출근 기록이 존재합니다. HR 관리자에게 문의해주세요."
                    },
                    status=400,
                )
        return Response(serializer.errors, status=400)


class ClockOutView(APIView):

    permission_classes = [IsSelfAttendance]

    def post(self, request, version):
        context = {"request": request}
        today = timezone.now()
        try:
            attendance = Attendance.objects.filter(employee=request.user).latest("date")
        except Attendance.DoesNotExist:
            return Response(
                {
                    "message": "금일 출근 기록이 확인되지 않았습니다. HR 관리자에게 문의주세요."
                },
                status=404,
            )
        if attendance.clock_out:
            return Response(
                {
                    "message": "금일 출근 기록이 이미 존재합니다. HR 관리자에게 문의주세요."
                },
                status=400,
            )
        # 본인 근태 기록인지 확인
        self.check_object_permissions(self.request, attendance)
        data = {"clock_out": today}
        if "clock_out_note" in request.data:
            data["clock_out_note"] = request.data.get("clock_out_note")
        serializer = AttendanceSerializer(
            attendance, data=data, partial=True, context=context
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "정상적으로 퇴근이 처리됐습니다.", "data": serializer.data}
            )
        return Response(serializer.errors, status=400)


class AttendanceUpdateView(APIView):

    permission_classes = [IsSelfAttendance]

    def patch(self, request, version, attendance_id):
        context = {"request": request}
        attendance = get_object_or_404(Attendance, id=attendance_id)
        # 본인 근태 기록인지 확인
        self.check_object_permissions(self.request, attendance)
        data = {}
        if "clock_in_note" in request.data:
            data["clock_in_note"] = request.data.get("clock_in_note")
        if "clock_out_note" in request.data:
            data["clock_out_note"] = request.data.get("clock_out_note")
        serializer = AttendanceSerializer(
            attendance, data=data, partial=True, context=context
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "성공적으로 수정됐습니다.", "data": serializer.data}
            )
        return Response({"errors": serializer.errors}, status=400)


# HR 어드민 View
class AdminAttendanceView(APIView):

    permission_classes = [IsHRAdmin]

    def get(self, request, version, user_id):
        context = {"request": request}
        # 'start_date', 'end_date' 없으면 오늘로 설정
        today = timezone.now().date()
        start_date = request.GET.get("start_date", today)
        end_date = request.GET.get("end_date", today)
        attendance = Attendance.objects.filter(
            Q(date__gte=start_date) & Q(date__lte=end_date) & Q(employee_id=user_id)
        )
        serializer = AttendanceSerializer(attendance, context=context, many=True)
        response_data = {
            "start_date": start_date,
            "end_date": end_date,
            "total_hours": 0,
            "data": serializer.data,
        }
        for att in serializer.data:
            if att["hours_worked"]:
                response_data["total_hours"] += att["hours_worked"]
        return Response(response_data)


class AdminAttendanceUpdateView(APIView):

    permission_classes = [IsHRAdmin]

    def patch(self, request, version, attendance_id):
        context = {"request": request}
        attendance = get_object_or_404(Attendance, id=attendance_id)
        serializer = AdminAttendanceSerializer(
            attendance, data=request.data, partial=True, context=context
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "성공적으로 수정됐습니다.", "data": serializer.data}
            )
        return Response({"errors": serializer.errors}, status=400)
