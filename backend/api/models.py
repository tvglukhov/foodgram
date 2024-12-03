from django.contrib.auth import get_user_model
from django.db import models

from .constants import CHARFIELD_MAX_LENGTH

User = get_user_model()


class Tag(models.Model):
    """Модель Тэга."""
    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH, unique=True)
    slug = models.CharField(max_length=CHARFIELD_MAX_LENGTH, unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class Ingredient(models.Model):
    """Модель Ингридиента."""
    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH)
    measurement_unit = models.CharField(max_length=CHARFIELD_MAX_LENGTH)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель Рецепта."""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes'
    )
    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH)
    image = models.TextField()
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient)
    tags = models.ManyToManyField(Tag)
    cooking_time = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredient(models.Model):
    """Модель, определяющая количество ингридиента для рецепта."""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField()
