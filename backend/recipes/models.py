import shortuuid

from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db import IntegrityError, models

from .constants import CHARFIELD_MAX_LENGTH

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
        User, on_delete=models.CASCADE, related_name='recipes'
    )
    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH)
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,  # Временно указал поле как пустое на время разработки
        default=None
    )
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient')
    tags = models.ManyToManyField(Tag)
    cooking_time = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredient(models.Model):
    """Модель, определяющая количество ингридиента для рецепта."""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipe_ingredient')
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE)
    amount = models.FloatField()


class ShoppingCart(models.Model):
    """Модель Списка покупок."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='cart_user'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )


class Favorite(models.Model):
    """Модель Избранных рецептов."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite'
    )


class ShortLinkRecipe(models.Model):
    """Модель прямых ссылок на рецепты."""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE)
    short_link_code = models.CharField(max_length=5,
                                       unique=True)

    @receiver(models.signals.post_save, sender=Recipe)
    def generate_short_link_code(sender, instance, created, **kwargs):
        """Создание короткого кода для Рецептов при создании Рецепта."""
        if created:
            while True:
                try:
                    ShortLinkRecipe.objects.create(
                        short_link_code=shortuuid.ShortUUID().random(length=10),
                        recipe_id=instance.id
                    )
                    break
                except IntegrityError:
                    pass

    def __str__(self):
        return self.short_link_code
