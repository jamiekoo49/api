from rest_framework.permissions import BasePermission

from accounts.models import Account


class DenyAny(BasePermission):
    def has_permission(self, request, view):
        return False

    def has_object_permission(self, request, view, obj):
        return False


class AllowSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        assert isinstance(obj, Account), f"Expected obj to be Account, got {type(obj)}"
        return obj.email == request.user.email


class AllowCoach(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "coach")


class AllowAthlete(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "athlete")


class AllowSameUniversity(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Ensure obj has posted_by and posted_by has university
        assert hasattr(obj, "posted_by"), f"Expected obj to have posted_by attribute, got {type(obj)}"
        assert hasattr(obj.posted_by, "university"), (
            f"Expected posted_by to have university attribute, got {type(obj.posted_by)}"
        )
        # Ensure request.user is a coach
        if not hasattr(request.user, "coach"):
            return False
        # Compare universities
        return obj.posted_by.university == request.user.coach.university
