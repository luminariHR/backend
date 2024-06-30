from django.conf import settings
from rest_framework import permissions


class IsHRAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.groups.filter(name=settings.HR_ADMIN_GROUP_NAME).exists()


class IsHRAdminOrSelf(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            obj == request.user
            or request.user.groups.filter(name=settings.HR_ADMIN_GROUP_NAME).exists()
        )
