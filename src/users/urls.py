from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, MyProfileView, UserInviteView

router = DefaultRouter()
router.register(r"accounts", EmployeeViewSet, basename="employee")

urlpatterns = [
    path("", include(router.urls)),
    path("me/", MyProfileView.as_view()),
    path("invite/", UserInviteView.as_view()),
]
