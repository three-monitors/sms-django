from rest_framework.permissions import BasePermission


class IsStaffOrAdmin(BasePermission):
    """Лише персонал та адміни"""

    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsOwnerOrReadOnly(BasePermission):
    """Змінювати може тільки автор або адмін"""

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS', 'POST']:
            return True
        return obj.created_by == request.user or request.user.is_superuser
