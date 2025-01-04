from django.contrib.auth import get_user_model
from django_filters import (AllValuesMultipleFilter,
                            ChoiceFilter,
                            FilterSet,
                            ModelChoiceFilter)
from rest_framework import filters

from .constants import RECIPE_IS_IN
from recipes.models import Recipe

User = get_user_model()


class FirstLetterFilter(filters.BaseFilterBackend):
    """Фильтр по частичному вхождению в поле name."""

    def filter_queryset(self, request, queryset, view):
        name = request.query_params.get('name')
        if name:
            return queryset.filter(name__istartswith=name)
        return queryset


class RecipeFilter(FilterSet):
    """Фильтрация для эндпоинта recipes."""

    author = ModelChoiceFilter(
        queryset=User.objects.all()
    )
    tags = AllValuesMultipleFilter(
        field_name='tags__slug',
        label='Ссылка'
    )

    is_in_shopping_cart = ChoiceFilter(
        choices=RECIPE_IS_IN,
        method='get_is_in'
    )
    is_favorited = ChoiceFilter(
        choices=RECIPE_IS_IN,
        method='get_is_in'
    )

    def get_is_in(self, queryset, name, value):
        """Фильтрация кверисета в зависимости от параметров запроса."""
        user = self.request.user
        if user.is_authenticated:
            if value == '1':
                if name == 'is_favorited':
                    queryset = queryset.filter(favorite__user=user)
                if name == 'is_in_shopping_cart':
                    queryset = queryset.filter(shopping_cart__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_in_shopping_cart', 'is_favorited')
