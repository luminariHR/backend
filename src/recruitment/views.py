from rest_framework import viewsets
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
