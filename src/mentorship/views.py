from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from django.db.models import Q
from users.models import Employee
from users.serializers import EmployeeSerializer
from core.permissions import IsHRAdmin
from .models import Mentor, Mentee, Match, Session
from .serializers import (
    MentorSerializer,
    MenteeSerializer,
    MatchSerializer,
    SessionSerializer,
)

from .recommendation import get_mentor_and_mentee_recommendations


# HR 관리자 View
class MentorsView(APIView):

    permission_classes = [IsHRAdmin]

    def get(self, request, version):
        context = {"request": request}
        mentors = Mentor.objects.all()
        serializer = MentorSerializer(mentors, context=context, many=True)
        return Response(serializer.data)

    def post(self, request, version):
        context = {"request": request}
        serializer = MentorSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "성공적으로 멘토가 추가됐습니다.",
                    "data": serializer.data,
                }
            )
        return Response({"errors": serializer.errors}, status=400)


class MentorView(APIView):

    permission_classes = [IsHRAdmin]

    def get(self, request, version, mentor_id):
        context = {"request": request}
        try:
            mentor = Mentor.objects.get(id=mentor_id)
        except Mentor.DoesNotExist:
            return Response(
                {"message": "존재하지 않는 멘토입니다."},
                status=404,
            )
        serializer = MentorSerializer(mentor, context=context)
        return Response(serializer.data)

    def delete(self, request, version, mentor_id):
        context = {"request": request}
        try:
            mentor = Mentor.objects.get(id=mentor_id)
        except Mentor.DoesNotExist:
            return Response(
                {"message": "존재하지 않는 멘토입니다."},
                status=404,
            )
        serializer = MentorSerializer(
            mentor, data=request.data, partial=True, context=context
        )
        serializer.delete(mentor)
        return Response({"message": "성공적으로 멘토를 제외했습니다."}, status=200)


class MenteesView(APIView):

    permission_classes = [IsHRAdmin]

    def get(self, request, version):
        context = {"request": request}
        mentees = Mentee.objects.all()
        serializer = MenteeSerializer(mentees, context=context, many=True)
        return Response(serializer.data)

    def post(self, request, version):
        context = {"request": request}
        serializer = MenteeSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "성공적으로 멘티가 추가됐습니다.",
                    "data": serializer.data,
                }
            )
        return Response({"errors": serializer.errors}, status=400)


class MenteeView(APIView):

    permission_classes = [IsHRAdmin]

    def get(self, request, version, mentee_id):
        context = {"request": request}
        try:
            mentee = Mentee.objects.get(id=mentee_id)
        except Mentee.DoesNotExist:
            return Response(
                {"message": "존재하지 않는 멘티입니다."},
                status=404,
            )
        serializer = MenteeSerializer(mentee, context=context)
        return Response(serializer.data)

    def delete(self, request, version, mentee_id):
        context = {"request": request}
        try:
            mentee = Mentee.objects.get(id=mentee_id)
        except Mentee.DoesNotExist:
            return Response(
                {"message": "존재하지 않는 멘티입니다."},
                status=404,
            )
        serializer = MenteeSerializer(
            mentee, data=request.data, partial=True, context=context
        )
        serializer.delete(mentee)
        return Response({"message": "성공적으로 멘티를 제외했습니다."}, status=200)


class AvailableEmployeesView(generics.ListAPIView):
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        mentor_ids = Mentor.objects.values_list("employee_id", flat=True)
        mentee_ids = Mentee.objects.values_list("employee_id", flat=True)
        return Employee.objects.exclude(id__in=mentor_ids).exclude(id__in=mentee_ids)


class MatchesView(APIView):

    permission_classes = [IsHRAdmin]

    def get(self, request, version):
        context = {"request": request}
        matches = Match.objects.all()
        serializer = MatchSerializer(matches, context=context, many=True)
        return Response(serializer.data)

    def post(self, request, version):
        context = {"request": request}
        serializer = MatchSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "성공적으로 매칭이 완료됐습니다.",
                    "data": serializer.data,
                }
            )
        return Response({"errors": serializer.errors}, status=400)


class SessionsView(APIView):

    permission_classes = [IsHRAdmin]

    def get(self, request, version, match_id):
        context = {"request": request}
        sessions = Session.objects.filter(match_id=match_id)
        serializer = SessionSerializer(sessions, context=context, many=True)
        return Response(serializer.data)

    def post(self, request, version, match_id):
        context = {"request": request}
        data = request.data.copy()
        data["match_id"] = match_id
        serializer = SessionSerializer(data=data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "성공적으로 세션이 추가됐습니다.",
                    "data": serializer.data,
                }
            )
        return Response({"errors": serializer.errors}, status=400)


# 기본 유저 View
class MyMatchHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        context = {"request": request}
        user = request.user
        matches_as_mentor = Match.objects.filter(mentor=user)
        matches_as_mentee = Match.objects.filter(mentee=user)

        matches = matches_as_mentor.union(matches_as_mentee)
        serializer = MatchSerializer(matches, many=True, context=context)
        return Response(serializer.data)


class MyCurrentMatchView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, version):
        context = {"request": request}
        user = request.user
        today = timezone.now().date()
        match = Match.objects.filter(
            (Q(mentor=user) | Q(mentee=user))
            & (Q(start_date__lte=today) & Q(end_date__gte=today))
        ).first()
        if not match:
            return Response(
                {"message": "현재 진행 중인 멘토링이 없습니다."},
                status=404,
            )
        serializer = MatchSerializer(match, context=context)
        return Response(serializer.data)


class MyMatchSessionsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, version):
        context = {"request": request}
        user = request.user
        today = timezone.now().date()
        match = Match.objects.filter(
            (Q(mentor=user)) & (Q(start_date__lte=today) & Q(end_date__gte=today))
        ).first()
        if not match:
            return Response(
                {"message": "현재 진행 중인 멘토링이 없습니다."},
                status=404,
            )
        sessions = Session.objects.filter(match_id=match.id)
        serializer = SessionSerializer(sessions, context=context, many=True)
        return Response(serializer.data)

    def post(self, request, version):
        context = {"request": request}
        user = request.user
        today = timezone.now().date()
        match = Match.objects.filter(
            (Q(mentor=user)) & (Q(start_date__lte=today) & Q(end_date__gte=today))
        ).first()
        if not match:
            return Response(
                {"message": "현재 진행 중인 멘토링이 없습니다."},
                status=404,
            )
        data = request.data.copy()
        data["match_id"] = match.id
        serializer = SessionSerializer(data=data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "성공적으로 세션이 추가됐습니다.",
                    "data": serializer.data,
                }
            )
        return Response({"errors": serializer.errors}, status=400)


class MentorRecommendationView(APIView):
    def get(self, request, *args, **kwargs):
        mentee_id = request.GET.get("mentee_id")
        if not mentee_id:
            return Response(
                {"message": "'mentee_id'는 필수 파라미터입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            mentee = Mentee.objects.get(employee_id=mentee_id)
        except Mentee.DoesNotExist:
            return Response(
                {"message": "존재하지 않는 멘티입니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 여기에 실제 추천 로직을 추가할 수 있습니다. 일단은 고정된 값으로 응답
        # recommendations = [1, 2, 3]
        result = get_mentor_and_mentee_recommendations(mentee_id)
        return Response(result)
