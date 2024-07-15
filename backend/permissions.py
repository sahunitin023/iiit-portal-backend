from rest_framework import permissions
from info.models import User


class IsFaculty(permissions.BasePermission):

    def has_permission(self, request, view):
        user: User = request.user
        if not user.is_authenticated:
            return False
        return user.is_faculty


class IsStudent(permissions.BasePermission):

    def has_permission(self, request, view):
        user: User = request.user
        if not user.is_authenticated:
            return False
        return user.is_student


class IsAdminOrStaff(permissions.BasePermission):

    def has_permission(self, request, view):
        user: User = request.user
        if not user.is_authenticated:
            return False
        return user.is_superuser or user.is_staff
