from rest_framework import serializers
from .models import *


class EssayQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EssayQuestion
        fields = "__all__"


class JobPostingSerializer(serializers.ModelSerializer):
    questions = EssayQuestionSerializer(many=True, read_only=True)
    number_of_applicants = serializers.SerializerMethodField()
    applicants = serializers.SerializerMethodField()

    class Meta:
        model = JobPosting
        fields = "__all__"

    def get_number_of_applicants(self, obj):
        return obj.number_of_applicants()

    def get_applicants(self, obj):
        return list(obj.applicants())


class EssayAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = EssayAnswer
        fields = "__all__"

    def validate(self, data):
        answer_text = data.get("answer_text", "")
        question = data.get("question")
        applicant_name = data.get("applicant_name")
        applicant_email = data.get("applicant_email")
        applicant_phone_number = data.get("applicant_phone_number")
        job_posting = data.get("job_posting")

        if question and len(answer_text) > question.max_length:
            raise serializers.ValidationError(
                f"Answer exceeds the maximum length of {question.max_length} characters for this question."
            )

        if EssayAnswer.objects.filter(
            job_posting=job_posting,
            applicant_name=applicant_name,
            applicant_email=applicant_email,
            applicant_phone_number=applicant_phone_number,
        ).exists():
            raise serializers.ValidationError(
                "You have already submitted answers for this job posting."
            )

        return data
