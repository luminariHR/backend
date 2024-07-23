from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from core.permissions import IsHRAdmin
from .models import *
from .serializers import *
from django.conf import settings
from rest_framework.decorators import action
from .tasks import summarize


class JobPostingViewSet(viewsets.ModelViewSet):
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer

    def get_queryset(self):
        if self.request.user.groups.filter(name=settings.HR_ADMIN_GROUP_NAME).exists():
            return JobPosting.objects.all()
        return JobPosting.objects.filter(status="open")

    def get_permissions(self):
        if self.request.user.groups.filter(name=settings.HR_ADMIN_GROUP_NAME).exists():
            return [IsHRAdmin() for _ in self.permission_classes]

        if self.request.method in ["GET"]:
            return [AllowAny()]

    def get_serializer_context(self):
        return {"request": self.request}

    @action(detail=True, methods=["patch"])
    def update_status(self, request, pk=None):
        job_posting = self.get_object()
        new_status = request.data.get("status")

        if new_status not in dict(JobPosting.STATUS_CHOICES).keys():
            return Response(
                {"detail": "Invalid status value."}, status=status.HTTP_400_BAD_REQUEST
            )

        job_posting.status = new_status
        job_posting.save()

        serializer = self.get_serializer(job_posting)
        return Response(serializer.data)


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
    allowed_methods = ["GET", "POST"]

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

            applicant_name = serializer.validated_data["applicant_name"]
            applicant_email = serializer.validated_data["applicant_email"]

            return Response(
                {"applicant_name": applicant_name, "applicant_email": applicant_email},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JobPostingApplicantsView(APIView):
    permission_classes = [IsHRAdmin]

    def get(self, request, posting_id, *args, **kwargs):
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

    def get(self, request, posting_id, applicant_email, *args, **kwargs):
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
        result = []
        for answer in answers:
            result.append(
                {
                    "question_id": answer.question.pk,
                    "answer": answer.answer_text,
                }
            )
        return Response(result, status=status.HTTP_200_OK)


class SummaryViewSet(viewsets.ModelViewSet):
    queryset = Summary.objects.all()
    serializer_class = SummarySerializer

    def list(self, request, *args, **kwargs):
        posting_id = request.query_params.get("posting_id")
        applicant_email = request.query_params.get("applicant_email")

        if posting_id and applicant_email:
            summary = Summary.objects.filter(
                job_posting__id=posting_id, applicant_email=applicant_email
            )
            if not summary.exists():
                return Response({"error": "Summary not found."}, status=404)
        else:
            return Response(
                {"error": "posting_id and applicant_email are required."}, status=400
            )

        serializer = self.get_serializer(summary, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
