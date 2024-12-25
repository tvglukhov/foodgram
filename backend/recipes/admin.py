from django.contrib import admin

from .models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShortLinkRecipe,
    Tag,
)


class IngredientsInRecipeInline(admin.StackedInline):
    """Инлайн ингредиентов в рецепте."""

    model = RecipeIngredient
    extra = 1


class ShortLinkInRecipe(admin.StackedInline):
    """Инлайн короткой ссылки в рецепте."""

    model = ShortLinkRecipe
    extra = 0
    can_delete = False
    max_num = 0


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройки представления модели Ingredient."""

    list_display = ('name', 'measurement_unit')
    list_display_links = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройки представления модели Tag."""

    list_display = ('name', 'slug')
    list_display_links = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройки представления модели Recipe."""

    inlines = (
        IngredientsInRecipeInline,
        ShortLinkInRecipe,
    )

    list_display = ('name', 'author')
    list_display_links = ('name',)
    list_filter = ('tags',)
    search_fields = ('name', 'author')
