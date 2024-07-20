import calendar
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from .serializers import PTOSerializer, DailyPTOSerializer, MonthlyPTOSerializer
from .models import PTO, PTOType


# 일반 회원 View
class MonthlyPTOView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, version):
        context = {"request": request}
        year = int(request.GET.get("year"))
        month = int(request.GET.get("month"))
        day = request.GET.get("day", None)
        if day is None:
            ptos = PTO.objects.filter(
                Q(status="approved")
                & (
                    (Q(start_date__year=year) & Q(start_date__month=month))
                    | (Q(end_date__year=year) & Q(end_date__month=month))
                )
            ).distinct()
            num_days = calendar.monthrange(year, month)[1]
            dates = [
                datetime(year, month, day).date() for day in range(1, num_days + 1)
            ]
            results = []
            for date in dates:
                filtered_ptos = ptos.filter(start_date__lte=date, end_date__gte=date)
                results.append(
                    {
                        "date": date,
                        "total_count": filtered_ptos.count(),
                    }
                )
            serializer = MonthlyPTOSerializer(results, context=context, many=True)
        else:
            day = int(day)
            date = datetime(year, month, day).date()
            ptos = PTO.objects.filter(
                status="approved", start_date__lte=date, end_date__gte=date
            ).distinct()
            employees = []
            for pto in ptos:
                employees.append(
                    {
                        "id": pto.employee.id,
                        "employee_id": pto.employee.employee_id,
                        "job_title": pto.employee.job_title,
                        "name": pto.employee.name,
                        "department": pto.employee.department,
                        "start_date": pto.start_date,
                        "end_date": pto.end_date,
                        "profile_image": pto.employee.profile_image,
                    }
                )
            results = {
                "date": date,
                "total_count": ptos.count(),
                "employees": employees,
            }
            serializer = DailyPTOSerializer(results, context=context)
        return Response(serializer.data)


class ReceivedPTORequestsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, version):
        context = {"request": request}
        user = self.request.user
        ptos = PTO.objects.filter(authorizer=user)
        serializer = PTOSerializer(ptos, context=context, many=True)
        return Response(serializer.data)


class PTOsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, version):
        context = {"request": request}
        user = self.request.user
        ptos = PTO.objects.filter(employee=user)
        pto_type = PTOType.objects.get(pto_type="default")
        strategy = pto_type.get_strategy()
        today = timezone.now().date()
        serializer = PTOSerializer(ptos, context=context, many=True)
        return Response(
            {
                "default_pto_left": strategy.ptos_left(user, today),
                "records": serializer.data,
            }
        )

    def post(self, request, version):
        context = {"request": request}
        pto_type = PTOType.objects.get(pto_type=request.data["pto_type"])
        request.data["pto_type"] = pto_type.id
        serializer = PTOSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "성공적으로 휴가가 신청 되었습니다.",
                    "data": serializer.data,
                }
            )
        return Response({"errors": serializer.errors}, status=400)


class PTOView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, version, pto_id):
        context = {"request": request}
        user = self.request.user
        try:
            pto = PTO.objects.get(
                Q(id=pto_id) & (Q(employee=user) | Q(authorizer=user))
            )
        except PTO.DoesNotExist:
            return Response(
                {"message": "존재하지 않는 휴가 요청입니다."},
                status=404,
            )
        serializer = PTOSerializer(pto, context=context)
        return Response(serializer.data)


class PTOReviewView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, version, pto_id):
        context = {"request": request}
        try:
            pto = PTO.objects.get(id=pto_id, authorizer=request.user)
        except PTO.DoesNotExist:
            return Response(
                {"message": "존재하지 않는 휴가 요청입니다."},
                status=404,
            )
        serializer = PTOSerializer(
            pto, data={"status": request.data["status"]}, partial=True, context=context
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "성공적으로 휴가 요청 검토가 완료되었습니다.",
                    "data": serializer.data,
                }
            )
        errors = []
        for e in serializer.errors.values():
            errors += e
        return Response({"errors": errors}, status=400)
