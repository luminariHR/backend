from abc import ABC, abstractmethod
from dateutil.relativedelta import relativedelta
from datetime import date
from .models import PTO


class BasePTOStrategy(ABC):
    @abstractmethod
    def calculate_pto(self, user, join_date, today):
        pass

    @abstractmethod
    def can_use_pto(self, user, today, start_date, end_date):
        pass


class UnrestrictedPTOStrategy(BasePTOStrategy):
    def calculate_pto(self, user, join_date, today):
        return 365

    def can_use_pto(self, user, today, start_date, end_date):
        return True


class DefaultPTOStrategy(BasePTOStrategy):
    def calculate_pto(self, user, join_date, today):
        employment_duration = relativedelta(today, join_date)

        if employment_duration.years < 1:
            return employment_duration.months + 1
        else:
            return 15 + employment_duration.years // 2

    def used_ptos_this_year(self, user, today):

        start_of_year = date(today.year, 1, 1)
        end_of_year = date(today.year, 12, 31)

        used_pto_this_year = PTO.objects.filter(
            employee=user,
            pto_type__pto_type="default",
            start_date__gte=start_of_year,
            start_date__lte=end_of_year,
            status="approved",
        ).count()

        return used_pto_this_year

    def ptos_left(self, user, today):

        return self.calculate_pto(
            user, user.start_date, today
        ) - self.used_ptos_this_year(user, today)

    def can_use_pto(self, user, today, start_date, end_date):

        start_of_month = date(today.year, 1, 1)
        end_of_month = date(today.year, 12, 31)

        used_pto_this_year = PTO.objects.filter(
            employee=user,
            pto_type__pto_type="default",
            start_date__gte=start_of_month,
            start_date__lte=end_of_month,
            status="approved",
        ).count()

        days_requested = (end_date - start_date).days + 1

        return used_pto_this_year + days_requested <= self.calculate_pto(
            user, user.start_date, today
        )


class FamilyCarePTOStrategy(BasePTOStrategy):
    def calculate_pto(self, user, join_date, today):
        return 10

    def can_use_pto(self, user, today, start_date, end_date):
        return True


class MaternityLeavePTOStrategy(BasePTOStrategy):
    def calculate_pto(self, user, join_date, today):
        return 60

    def can_use_pto(self, user, today, start_date, end_date):
        if user.gender == 0:
            return False
        return True


class PaternityLeavePTOStrategy(BasePTOStrategy):
    def calculate_pto(self, user, join_date, today):
        return 10

    def can_use_pto(self, user, today, start_date, end_date):
        if user.gender == 0:
            return True
        return False


class RefreshPTOStrategy(BasePTOStrategy):
    def calculate_pto(self, user, join_date, today):
        return 4

    def can_use_pto(self, user, today, start_date, end_date):
        return True


class MenstrualPeriodLeavePTOStrategy(BasePTOStrategy):
    def calculate_pto(self, user, join_date, today):
        return 12

    def can_use_pto(self, user, today, start_date, end_date):
        if user.gender == 0:
            return False
        return True
