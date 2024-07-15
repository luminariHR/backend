from rest_framework import serializers
from .models import *


class EssayQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EssayQuestion
        fields = "__all__"


class JobPostingSerializer(serializers.ModelSerializer):
    questions = EssayQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = JobPosting
        fields = "__all__"


class EssayAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = EssayAnswer
        fields = "__all__"

    def validate(self, data):
        answer_text = data.get("answer_text", "")
        question = data.get("question")
        applicant_name = data.get("applicant_name")
        applicant_ssn = data.get("applicant_ssn")
        job_posting = data.get("job_posting")

        if question and len(answer_text) > question.max_length:
            raise serializers.ValidationError(
                f"Answer exceeds the maximum length of {question.max_length} characters for this question."
            )

        if EssayAnswer.objects.filter(
            job_posting=job_posting,
            applicant_name=applicant_name,
            applicant_ssn=applicant_ssn,
        ).exists():
            raise serializers.ValidationError(
                "You have already submitted answers for this job posting."
            )

        return data
