from django.urls import path
from .views import DepartmentListView, DepartmentView

urlpatterns = [
    path("", DepartmentListView.as_view()),
    path("<int:dept_id>", DepartmentView.as_view()),
]
