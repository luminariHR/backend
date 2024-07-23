from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from users.models import Employee
from .models import Mentor, Mentee, Match
from .serializers import MentorSerializer, MenteeSerializer, MatchSerializer
from users.serializers import EmployeeSerializer
from .recommendation import get_mentor_and_mentee_recommendations


class MentorCreateView(generics.CreateAPIView):
    queryset = Mentor.objects.all()
    serializer_class = MentorSerializer


class MenteeCreateView(generics.CreateAPIView):
    queryset = Mentee.objects.all()
    serializer_class = MenteeSerializer


class MenteeListView(generics.ListAPIView):
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        mentee_ids = Mentee.objects.values_list("employee_id", flat=True)
        return Employee.objects.filter(id__in=mentee_ids)


class MentorListView(generics.ListAPIView):
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        mentor_ids = Mentor.objects.values_list("employee_id", flat=True)
        return Employee.objects.filter(id__in=mentor_ids)


class AvailableEmployeesView(generics.ListAPIView):
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        mentor_ids = Mentor.objects.values_list("employee_id", flat=True)
        mentee_ids = Mentee.objects.values_list("employee_id", flat=True)
        return Employee.objects.exclude(id__in=mentor_ids).exclude(id__in=mentee_ids)


class MatchCreateView(generics.CreateAPIView):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer


class MatchListView(generics.ListAPIView):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer


class MatchUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        matches_as_mentor = Match.objects.filter(mentor=user)
        matches_as_mentee = Match.objects.filter(mentee=user)

        matches = matches_as_mentor.union(matches_as_mentee)
        serializer = MatchSerializer(matches, many=True)
        return Response(serializer.data)


class MatchDeleteView(generics.DestroyAPIView):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    lookup_field = "id"


class MentorRecommendationView(APIView):
    def get(self, request, *args, **kwargs):
        mentee_id = request.GET.get("mentee_id")
        if not mentee_id:
            return Response(
                {"detail": "mentee_id parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            mentee = Mentee.objects.get(employee_id=mentee_id)
        except Mentee.DoesNotExist:
            return Response(
                {"detail": "Mentee with this ID does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 여기에 실제 추천 로직을 추가할 수 있습니다. 일단은 고정된 값으로 응답
        # recommendations = [1, 2, 3]
        get_mentor_and_mentee_recommendations(mentee_id)
        return Response(1)
