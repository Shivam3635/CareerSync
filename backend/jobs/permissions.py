from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """
    Allows access only to authenticated admin users (role == 'admin' or is_staff).
    Enforced strictly server-side.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (getattr(request.user, 'role', '') == 'admin' or request.user.is_staff)
        )
