from django.urls import path
from .views import AdminDepartmentMembersView

urlpatterns = [
    path("", AdminDepartmentMembersView.as_view()),
]
