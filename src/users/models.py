import calendar
from datetime import date
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext as _
from django.contrib.auth.models import BaseUserManager
from attendance.models import Attendance
from events.models import Event


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

    def get_years_of_service(self, current_date):
        years_of_service = current_date.year - self.start_date.year
        if current_date.month < self.start_date.month or (
            self.start_date.month == current_date.month
            and current_date.day < self.start_date.day
        ):
            years_of_service -= 1
        return years_of_service

    @staticmethod
    def get_working_days_in_month(year, month):
        _, num_days = calendar.monthrange(year, month)
        working_days = []
        for day in range(1, num_days + 1):
            current_day = date(year, month, day)
            if current_day.weekday() not in (5, 6):
                working_days.append(current_day)
        return working_days

    @staticmethod
    def get_company_holidays(year, month):
        company_holidays = Event.objects.filter(
            start_date__year=year, start_date__month=month, tag="public_holiday"
        ).values("start_date")
        holiday_set = {record["start_date"] for record in company_holidays}
        return holiday_set

    def get_days_of_absence(self, year, month):
        days_in_month = self.get_working_days_in_month(year, month)
        company_holidays = self.get_company_holidays(year, month)
        attendance_records = Attendance.objects.filter(
            employee=self, date__year=year, date__month=month
        ).values("date")
        attendance_set = {record["date"] for record in attendance_records}
        absences = 0
        for day in days_in_month:
            if day not in attendance_set and day not in company_holidays:
                absences += 1
        return absences

    @property
    def name(self):
        return f"{self.last_name}{self.first_name}"

    @property
    def legal_paid_time_off(self):
        # TODO: 입사일 기준으로 먼저 구현
        current_date = date.today()
        # 아직 입사일이 되지 않았으면, 연차 0일
        if current_date < self.start_date:
            return 0
        years_of_service = self.get_years_of_service(current_date)
        # 근로기간이 1년 미만인 경우, 1개월 만근마다 1일의 연차가 주어짐
        if years_of_service < 1:
            months_of_service = (
                (current_date.year - self.start_date.year) * 12
                + current_date.month
                - self.start_date.month
            )
            ranges = []
            end_month = (
                current_date.month + 1
                if self.start_date.day < current_date.day
                else current_date.month
            )
            if self.start_date.year < current_date.year:
                for month in range(self.start_date.month + 1, 13):
                    ranges.append((self.start_date.year, month))
                for month in range(1, end_month):
                    ranges.append((current_date.year, month))
            else:
                for month in range(self.start_date.month + 1, end_month):
                    ranges.append((current_date.year, month))
            ptos = len(ranges)
            for year, month in ranges:
                if self.get_days_of_absence(year, month) > 0:
                    ptos -= 1
            return ptos
        # 근로기간 1년 이상 3년 미만인 경우, 15일의 연차가 주어짐
        elif 1 <= years_of_service < 3:
            return 15
        # 근로기간 3년 이상인 경우, 최초 1년을 초과하는 매 2년 마다 1일을 가산한 연차가 추가로 주어짐 (최대 25일 한도)
        else:
            return max(25, 15 + (years_of_service - 1) // 2)
