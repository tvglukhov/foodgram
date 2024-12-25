import shortuuid

from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db import IntegrityError, models

from .constants import CHARFIELD_MAX_LENGTH, SHORTLINK_MAX_LENGTH

User = get_user_model()


class Tag(models.Model):
    """Модель Тэга."""
    name = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        unique=True,
        verbose_name='Название'
    )
    slug = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель Ингридиента."""
    name = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        verbose_name='ед. изм'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель Рецепта."""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH,
                            verbose_name='Название')
    image = models.ImageField(
        upload_to='recipes/images/',
        default=None,
        verbose_name='Изображение'
    )
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',
                                         verbose_name='Ингредиенты')
    tags = models.ManyToManyField(Tag,
                                  verbose_name='Тэги')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (мин)'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель, определяющая количество ингридиента для рецепта."""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipe_ingredient',
        verbose_name='Рецепт')
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.FloatField(verbose_name='Кол-во')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.ingredient.name}, {self.ingredient.measurement_unit}'


class ShoppingCart(models.Model):
    """Модель Списка покупок."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='cart_user',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Корзина покупок'
    )

    class Meta:
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'

    def __str__(self):
        return self.recipe.name


class Favorite(models.Model):
    """Модель Избранных рецептов."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранном'

    def __str__(self):
        return self.recipe.name


class ShortLinkRecipe(models.Model):
    """Модель прямых ссылок на рецепты."""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт')
    short_link_code = models.CharField(max_length=CHARFIELD_MAX_LENGTH,
                                       unique=True,
                                       verbose_name='Код ссылки')

    @receiver(models.signals.post_save, sender=Recipe)
    def generate_short_link_code(sender, instance, created, **kwargs):
        """Создание короткого кода для Рецептов при создании Рецепта."""
        if created:
            while True:
                try:
                    ShortLinkRecipe.objects.create(
                        short_link_code=shortuuid.ShortUUID().random(
                            length=SHORTLINK_MAX_LENGTH
                        ),
                        recipe_id=instance.id
                    )
                    break
                except IntegrityError:
                    pass

    class Meta:
        verbose_name = 'Короткая ссылка на рецепт'
        verbose_name_plural = 'Короткая ссылка на рецепт'

    def __str__(self):
        return self.recipe.name
