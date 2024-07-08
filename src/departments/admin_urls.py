from django.urls import path
from .views import AdminDepartmentCreateView, AdminDepartmentUpdateView

urlpatterns = [
    path("", AdminDepartmentCreateView.as_view()),
    path("<int:department_id>", AdminDepartmentUpdateView.as_view()),
]
