from django.shortcuts import get_object_or_404, redirect
from django.views import View

from recipes.models import ShortLinkRecipe


class RedirectShortLinkView(View):
    """Перенаправление с прямой ссылки на страницу Рецепта."""

    def get(self, request, short_link):
        """Обработка GET запроса через прямую ссылку на Рецепт."""
        short_link = get_object_or_404(
            ShortLinkRecipe,
            short_link_code=short_link
        )
        return redirect(
            request.build_absolute_uri(f'/recipes/{short_link.recipe_id}/')
        )
