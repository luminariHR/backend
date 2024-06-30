from django.contrib import admin

from .models import Employee


class EmployeeAdmin(admin.ModelAdmin):
    filter_horizontal = ("groups", "user_permissions")


admin.site.register(Employee, EmployeeAdmin)
