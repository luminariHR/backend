from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext as _
from django.contrib.auth.models import BaseUserManager
from PIL import Image


def user_directory_path(instance, filename):
    ext = filename.split(".")[-1]
    return f"profile/user_{instance.id}/profile.{ext}"


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
    profile_image = models.ImageField(
        upload_to=user_directory_path, blank=True, null=True
    )
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
    skills = models.JSONField(default=list, null=True, blank=True)
    certifications = models.JSONField(default=list, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    mbti = models.CharField(max_length=4, null=True, blank=True)
    hobbies = models.JSONField(default=list, null=True, blank=True)
    # Auth
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = EmployeeManager()

    @property
    def name(self):
        return f"{self.last_name}{self.first_name}"

    def is_ooo(self):
        ptos = self.ptos
        today = timezone.now().date()
        return ptos.filter(
            status="approved", start_date__gte=today, end_date__lte=today
        ).exists()

    def resize_profile_image(self):
        img = Image.open(self.profile_image.path)
        max_size = (400, 400)
        img.thumbnail(max_size, Image.LANCZOS)
        img.save(self.profile_image.path)

    def save(self, *args, **kwargs):
        try:
            employee = Employee.objects.get(id=self.id)
            if (
                employee.profile_image != self.profile_image
                and employee.profile_image.name
            ):
                employee.profile_image.delete(save=False)
        except Employee.DoesNotExist:
            pass
        super().save(*args, **kwargs)
        if self.profile_image:
            self.resize_profile_image()


class Project(models.Model):
    title = models.CharField(max_length=100)
    role = models.CharField(max_length=50)
    duration = models.CharField(max_length=50)
    description = models.TextField()
    employee = models.ForeignKey(
        Employee, related_name="projects", on_delete=models.CASCADE
    )
