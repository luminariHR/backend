from django.db import models


class JobPosting(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    position = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class EssayQuestion(models.Model):
    job_posting = models.ForeignKey(
        JobPosting, related_name="questions", on_delete=models.CASCADE
    )
    question_text = models.TextField()
    max_length = models.IntegerField()

    def __str__(self):
        return self.question_text


class EssayAnswer(models.Model):
    job_posting = models.ForeignKey(
        JobPosting, related_name="answers", on_delete=models.CASCADE
    )
    question = models.ForeignKey(
        EssayQuestion, related_name="answers", on_delete=models.CASCADE
    )
    applicant_name = models.CharField(max_length=255)
    applicant_ssn = models.CharField(max_length=14)
    answer_text = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["job_posting", "applicant_name", "applicant_ssn"],
                name="unique_applicant_application",
            )
        ]

    def __str__(self):
        return f"{self.applicant_name} - {self.question.question_text}"
