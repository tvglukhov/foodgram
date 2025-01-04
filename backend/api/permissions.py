from rest_framework.permissions import BasePermission, SAFE_METHODS


class AllowAnyExceptEndpointMe(BasePermission):
    """Разрешает анонимным всё, кроме эндпоинта /api/user/me/."""

    def has_permission(self, request, view):
        if request.path == '/api/users/me/' and request.user.is_anonymous:
            return False
        return super().has_permission(request, view)


class AuthorOrReadOnly(BasePermission):
    """Только чтение, редактирование доступно только автору."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated
                and (request.user == obj.author
                     or request.user.is_superuser))
