from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext as _
from django.contrib.auth.models import BaseUserManager


class EmployeeManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user


class Employee(AbstractUser):

    # gender
    MALE = 0
    FEMALE = 1
    GENDER_CHOICES = (
        (MALE, "Male"),
        (FEMALE, "Female"),
    )

    # employment status
    ACTIVE = 0
    ON_LEAVE = 1
    TERMINATED = 2

    EMPLOYMENT_STATUS_CHOICES = (
        (ACTIVE, "Active"),
        (ON_LEAVE, "On Leave"),
        (TERMINATED, "Terminated"),
    )
    username = None
    email = models.EmailField(verbose_name=_("email address"), unique=True)
    employee_id = models.CharField(max_length=50)
    gender = models.IntegerField(choices=GENDER_CHOICES, default=0)
    employment_status = models.IntegerField(
        default=0, choices=EMPLOYMENT_STATUS_CHOICES
    )
    job_title = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=50, null=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    department = models.ForeignKey(
        "departments.Department",
        related_name="members",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # Auth
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = EmployeeManager()

    @property
    def name(self):
        return f"{self.last_name}{self.first_name}"
