import uuid
from django.db import models
from django.utils import timezone
from core.models import AbstractBaseModel
from users.models import Employee


def pto_document_directory_path(instance, filename):
    return f"pto/{instance.id}/{filename}"


class PTOType(AbstractBaseModel):
    name = models.TextField()
    pto_type = models.CharField(max_length=100)
    strategy_class = models.CharField(
        max_length=255, default="strategies.DefaultPTOStrategy"
    )

    PTO_STRATEGY_MAPPING = {
        "default": "strategies.DefaultPTOStrategy",
        "family_care": "strategies.FamilyCarePTOStrategy",
        "maternity_leave": "strategies.MaternityLeavePTOStrategy",
        "paternity_leave": "strategies.PaternityLeavePTOStrategy",
        "menstrual_period_leave": "strategies.MenstrualPeriodLeavePTOStrategy",
        "refresh_leave": "strategies.RefreshPTOStrategy",
        "sick_leave": "strategies.UnrestrictedPTOStrategy",
    }

    def __str__(self):
        return self.name

    def get_strategy(self):
        module_name, class_name = self.strategy_class.rsplit(".", 1)
        module = __import__("ptos." + module_name, fromlist=[class_name])
        return getattr(module, class_name)()

    def get_strategy_class(self, pto_type):
        if pto_type.lower() in self.PTO_STRATEGY_MAPPING:
            return self.PTO_STRATEGY_MAPPING[pto_type.lower()]
        return "strategies.UnrestrictedPTOStrategy"

    def save(self, *args, **kwargs):
        self.strategy_class = self.get_strategy_class(self.pto_type)
        super().save(*args, **kwargs)


class PTO(AbstractBaseModel):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="ptos"
    )
    pto_type = models.ForeignKey(PTOType, on_delete=models.CASCADE, related_name="ptos")
    start_date = models.DateField()
    end_date = models.DateField()
    authorizer = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="ptos_approved"
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    message = models.TextField(blank=True, null=True)
    file = models.FileField(
        upload_to=pto_document_directory_path, blank=True, null=True
    )

    def __str__(self):
        return f"{self.employee.name} - {self.pto_type.name} ({self.start_date} to {self.end_date})"

    def save(self, *args, **kwargs):
        self.clean()
        today = timezone.now().date()
        strategy = self.pto_type.get_strategy()
        if strategy.can_use_pto(self.employee, today, self.start_date, self.end_date):
            super().save(*args, **kwargs)

    def clean(self):
        super().clean()

    def get_pto_type_display(self, obj):
        return obj.pto_type.pto_type
