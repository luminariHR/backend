"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path("admin/", admin.site.urls),
    # 부서
    re_path(r"api/(?P<version>(v1))/departments/", include("departments.urls")),
    re_path(
        r"api/(?P<version>(v1))/admin/departments/", include("departments.admin_urls")
    ),
    # 인사 발령 (부서, 직책)
    re_path(
        r"api/(?P<version>(v1))/admin/appointments/", include("appointments.admin_urls")
    ),
    # 주별 업무
    re_path(r"api/(?P<version>(v1))/todo/", include("todos.urls")),
    # re_path(r"api/(?P<version>(v1))/admin/todos/", include("todos.admin_urls")),
    # 근태 관리
    re_path(r"api/(?P<version>(v1))/attendance/", include("attendance.urls")),
    # re_path(r"api/(?P<version>(v1))/admin/attendance/", include("todos.admin_urls")),
    # 일정 관리
    re_path(r"api/(?P<version>(v1))/events/", include("events.urls")),
    re_path(r"api/(?P<version>(v1))/admin/events/", include("events.admin_urls")),
    re_path(r"api/(?P<version>(v1))/", include("users.urls")),
    re_path(
        r"api/(?P<version>(v1|v2))/token/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    re_path(
        r"api/(?P<version>(v1|v2))/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    re_path(r"api/(?P<version>(v1|v2))/messenger/", include("messenger.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
