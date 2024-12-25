from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Subscribe
from recipes.models import (
    Favorite,
    ShoppingCart,
)

User = get_user_model()


class SubscribeInUser(admin.StackedInline):
    """Инлайн подписок Пользователя."""

    model = Subscribe
    fk_name = 'user'
    extra = 0
    max_num = 0


class FavoriteInUser(admin.StackedInline):
    """Инлайн избранного Пользователя."""

    model = Favorite
    fk_name = 'user'
    extra = 0
    max_num = 0


class ShoppingCartInUser(admin.StackedInline):
    """Инлайн корзины покупок Пользователя."""

    model = ShoppingCart
    fk_name = 'user'
    extra = 0
    max_num = 0


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Настройки представления модели User."""

    inlines = (
        FavoriteInUser,
        ShoppingCartInUser,
        SubscribeInUser,
    )

    list_display = ('username', 'first_name', 'last_name', 'email',)
    exclude = ('password', 'groups')
    search_fields = ('username', 'email',)
