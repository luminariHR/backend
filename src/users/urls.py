from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, MyProfileView

router = DefaultRouter()
router.register(r"accounts", EmployeeViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("me/", MyProfileView.as_view()),
]
