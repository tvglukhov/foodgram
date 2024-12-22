from rest_framework.permissions import BasePermission


class IsAuthenticatedOrReadOnly(BasePermission):
    """Только чтение, редактирование доступно пользовтелям."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class AllowAnyExceptEndpointMe(BasePermission):
    """Разрешает анонимным всё, кроме эндпоинта /api/user/me/."""

    def has_permission(self, request, view):
        if request.path == '/api/users/me/' and request.user.is_anonymous:
            return False
        return super().has_permission(request, view)
