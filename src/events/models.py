from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime
from core.models import AbstractBaseModel


class Event(AbstractBaseModel):

    COMPANY_EVENT = "company_event"
    FAMILY_EVENT = "family_event"
    CERTIFICATE = "certificate"
    EXTERNAL_EVENT = "external_event"
    PUBLIC_HOLIDAY = "public_holiday"
    OTHERS = "others"

    TAG_CHOICES = (
        (COMPANY_EVENT, "Company Event"),
        (FAMILY_EVENT, "Family Event"),
        (CERTIFICATE, "Certificate"),
        (EXTERNAL_EVENT, "External Event"),
        (PUBLIC_HOLIDAY, "Public Holiday"),
        (OTHERS, "Others"),
    )

    title = models.CharField(max_length=20)
    content = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    tag = models.CharField(max_length=20, choices=TAG_CHOICES, default=OTHERS)
    author = models.ForeignKey(
        "users.Employee", on_delete=models.CASCADE, related_name="events_created"
    )
    # TODO: images 추가

    class Meta:
        ordering = ["start_date"]

    def clean(self):
        super().clean()
        if self.end_date < self.start_date:
            raise ValidationError("종료일이 시작일보다 빠를 수 없습니다.")
        if (self.start_time or self.end_time) and not (
            self.start_time and self.end_time
        ):
            raise ValidationError("시작 시간과 종료 시간을 둘 다 설정해야 합니다.")
        if self.start_time and self.end_time:
            start_datetime = datetime.combine(self.start_date, self.start_time)
            end_datetime = datetime.combine(self.end_date, self.end_time)
            if end_datetime < start_datetime:
                raise ValidationError("종료일시가 시작일시보다 빠를 수 없습니다.")

    def __str__(self):
        return f"{self.title} - {self.author}"
