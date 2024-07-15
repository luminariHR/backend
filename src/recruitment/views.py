from rest_framework import viewsets
from .models import *
from .serializers import *


class JobPostingViewSet(viewsets.ModelViewSet):
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer


class EssayQuestionViewSet(viewsets.ModelViewSet):
    queryset = EssayQuestion.objects.all()
    serializer_class = EssayQuestionSerializer


class EssayAnswerViewSet(viewsets.ModelViewSet):
    queryset = EssayAnswer.objects.all()
    serializer_class = EssayAnswerSerializer
