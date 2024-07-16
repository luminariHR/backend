from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from core.permissions import IsHRAdmin
from .models import *
from .serializers import *


class JobPostingViewSet(viewsets.ModelViewSet):
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer
    permission_classes = [IsHRAdmin]


class EssayQuestionViewSet(viewsets.ModelViewSet):
    queryset = EssayQuestion.objects.all()
    serializer_class = EssayQuestionSerializer
    permission_classes = [IsHRAdmin]


class EssayAnswerViewSet(viewsets.ModelViewSet):
    queryset = EssayAnswer.objects.all()
    serializer_class = EssayAnswerSerializer
    permission_classes = [AllowAny]


class AnswerView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, posting_id, *args, **kwargs):
        try:
            job_posting = JobPosting.objects.get(id=posting_id)
        except JobPosting.DoesNotExist:
            return Response(
                {"error": "JobPosting not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = JobPostingSerializer(job_posting)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, posting_id, *args, **kwargs):
        data = request.data.copy()
        data["posting_id"] = posting_id
        serializer = EssayAnswerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JobPostingApplicantsView(APIView):
    permission_classes = [IsHRAdmin]

    def get(self, request, posting_id):
        try:
            job_posting = JobPosting.objects.get(id=posting_id)
        except JobPosting.DoesNotExist:
            return Response(
                {"error": "JobPosting not found"}, status=status.HTTP_404_NOT_FOUND
            )

        answer = (
            EssayAnswer.objects.filter(job_posting=job_posting)
            .values("applicant_name", "applicant_email", "applicant_phone_number")
            .distinct()
        )

        return Response(answer, status=status.HTTP_200_OK)


class ApplicantEssayAnswersView(APIView):
    permission_classes = [IsHRAdmin]

    def get(self, request, posting_id, applicant_email):
        try:
            job_posting = JobPosting.objects.get(id=posting_id)
        except JobPosting.DoesNotExist:
            return Response(
                {"error": "JobPosting not found"}, status=status.HTTP_404_NOT_FOUND
            )

        answers = EssayAnswer.objects.filter(
            job_posting=job_posting, applicant_email=applicant_email
        )

        if not answers.exists():
            return Response(
                {"error": "No answers found for this applicant"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EssayAnswerSerializer(answers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
