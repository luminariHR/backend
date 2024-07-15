from django.db import models


class JobPosting(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    position = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    def number_of_applicants(self):
        return (
            EssayAnswer.objects.filter(job_posting=self)
            .values("applicant_email")
            .distinct()
            .count()
        )

    def applicants(self):
        return (
            EssayAnswer.objects.filter(job_posting=self)
            .values("applicant_name", "applicant_email", "applicant_phone_number")
            .distinct()
        )


class EssayQuestion(models.Model):
    job_posting = models.ForeignKey(
        JobPosting, related_name="questions", on_delete=models.CASCADE
    )
    question_text = models.TextField()
    max_length = models.IntegerField()

    def __str__(self):
        return self.question_text

    def create(self, validated_data):
        questions_data = validated_data.pop("questions", [])
        job_posting = JobPosting.objects.create(**validated_data)

        for question_data in questions_data:
            EssayQuestion.objects.create(job_posting=job_posting, **question_data)

        return job_posting

    def update(self, instance, validated_data):
        questions_data = validated_data.pop("questions", [])
        for question_data in questions_data:
            question_id = question_data.get("id")
            if question_id:
                question = EssayQuestion.objects.get(
                    id=question_id, job_posting=instance
                )
                for attr, value in question_data.items():
                    setattr(question, attr, value)
                question.save()
            else:
                EssayQuestion.objects.create(job_posting=instance, **question_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class EssayAnswer(models.Model):
    job_posting = models.ForeignKey(
        JobPosting, related_name="answers", on_delete=models.CASCADE
    )
    question = models.ForeignKey(
        EssayQuestion, related_name="answers", on_delete=models.CASCADE
    )
    applicant_name = models.CharField(max_length=255)
    applicant_email = models.EmailField(max_length=255)
    applicant_phone_number = models.CharField(max_length=15)
    answer_text = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "job_posting",
                    "applicant_name",
                    "applicant_email",
                    "applicant_phone_number",
                ],
                name="unique_applicant_application",
            )
        ]

    def __str__(self):
        return f"{self.applicant_name} - {self.question.question_text}"
