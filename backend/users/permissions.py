from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrAdmin(BasePermission):
    """
    يسمح فقط للمالك أو الـ admin بالتعديل.
    القراءة مسموحة للجميع المصادَق عليهم.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return obj == request.user or request.user.is_staff or request.user.is_superuser


class IsVerifiedUser(BasePermission):
    """يسمح فقط للمستخدمين الذين تم التحقق منهم."""

    message = "Your account must be verified to perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_verified
        )