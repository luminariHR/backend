from rest_framework import serializers
from .models import *


class EssayQuestionSerializer(serializers.ModelSerializer):
    job_posting = serializers.PrimaryKeyRelatedField(
        queryset=JobPosting.objects.all(), required=False
    )

    class Meta:
        model = EssayQuestion
        fields = ["id", "job_posting", "question_text", "max_length"]


class JobPostingSerializer(serializers.ModelSerializer):
    questions = EssayQuestionSerializer(many=True, required=False)
    number_of_applicants = serializers.SerializerMethodField()
    applicants = serializers.SerializerMethodField()

    class Meta:
        model = JobPosting
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        request = self.context.get("request")
        if (
            request
            and not request.user.groups.filter(
                name=settings.HR_ADMIN_GROUP_NAME
            ).exists()
        ):
            representation.pop("number_of_applicants", None)
            representation.pop("applicants", None)

        return representation

    def get_number_of_applicants(self, obj):
        return obj.number_of_applicants()

    def get_applicants(self, obj):
        return list(obj.applicants())

    def create(self, validated_data):
        questions_data = validated_data.pop("questions", [])
        job_posting = JobPosting.objects.create(**validated_data)

        for question_data in questions_data:
            EssayQuestion.objects.create(job_posting=job_posting, **question_data)

        return job_posting

    # def update(self, instance, validated_data):
    #     questions_data = validated_data.pop("questions", [])
    #     existing_questions = {
    #         question.id: question for question in instance.questions.all()
    #     }

    #     for question_data in questions_data:
    #         question_id = question_data.get("id")
    #         if question_id:
    #             if question_id in existing_questions:
    #                 question = existing_questions.pop(question_id)
    #                 for attr, value in question_data.items():
    #                     setattr(question, attr, value)
    #                 question.save()
    #         else:
    #             EssayQuestion.objects.create(job_posting=instance, **question_data)

    #     for question_id, question in existing_questions.items():
    #         question.delete()

    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)
    #     instance.save()
    #     return instance


class EssayAnswerSerializer(serializers.ModelSerializer):
    posting_id = serializers.IntegerField(write_only=True)
    applicant_name = serializers.CharField(max_length=255, write_only=True)
    applicant_email = serializers.EmailField(max_length=255, write_only=True)
    applicant_phone_number = serializers.CharField(max_length=15, write_only=True)
    answers = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField())
    )

    class Meta:
        model = EssayAnswer
        fields = [
            "posting_id",
            "applicant_name",
            "applicant_email",
            "applicant_phone_number",
            "answers",
        ]

    def validate(self, data):
        posting_id = data.get("posting_id")
        try:
            job_posting = JobPosting.objects.get(id=posting_id)

            if job_posting.status != "open":
                raise serializers.ValidationError(
                    "This job posting is not currently open."
                )

        except JobPosting.DoesNotExist:
            raise serializers.ValidationError(
                f"Job Posting with ID {posting_id} does not exist."
            )

        for answer in data["answers"]:
            question_id = answer.get("question_id")
            if not question_id:
                raise serializers.ValidationError(
                    "Each answer must include a question_id."
                )
            question = EssayQuestion.objects.filter(
                id=question_id, job_posting_id=posting_id
            ).first()
            if not question:
                raise serializers.ValidationError(
                    f"Question with ID {question_id} does not exist."
                )
            answer_text = answer.get("answer_text", "")
            if len(answer_text) > question.max_length:
                raise serializers.ValidationError(
                    f"Answer for question ID {question_id} exceeds the maximum length of {question.max_length} characters."
                )
            if not answer_text:
                raise serializers.ValidationError(
                    "You have to answer all the questions."
                )

            if EssayAnswer.objects.filter(
                job_posting=job_posting,
                question=question,
                applicant_name=data["applicant_name"],
                applicant_email=data["applicant_email"],
                applicant_phone_number=data["applicant_phone_number"],
            ).exists():
                raise serializers.ValidationError(
                    f"Answer for question ID {question_id} already exists for this applicant."
                )

        return data

    def create(self, validated_data):
        posting_id = validated_data.pop("posting_id")
        applicant_name = validated_data.pop("applicant_name")
        applicant_email = validated_data.pop("applicant_email")
        applicant_phone_number = validated_data.pop("applicant_phone_number")
        answers_data = validated_data.pop("answers")

        job_posting = JobPosting.objects.get(id=posting_id)
        created_answers = []

        for answer_data in answers_data:
            question_id = answer_data.get("question_id")
            answer_text = answer_data.get("answer_text")
            question = EssayQuestion.objects.get(id=question_id)

            essay_answer = EssayAnswer.objects.create(
                job_posting=job_posting,
                question=question,
                applicant_name=applicant_name,
                applicant_email=applicant_email,
                applicant_phone_number=applicant_phone_number,
                answer_text=answer_text,
            )

            created_answers.append(essay_answer)

        return {
            "posting_id": posting_id,
            "applicant_name": applicant_name,
            "applicant_email": applicant_email,
            "applicant_phone_number": applicant_phone_number,
            "answers": created_answers,
        }


class SummarySerializer(serializers.ModelSerializer):
    # job_posting = JobPostingSerializer()

    class Meta:
        model = Summary
        fields = ["summarys", "techs", "jobs", "questions"]
