from django.contrib.auth.models import AbstractUser
from django.db import models


class FoodgramUser(AbstractUser):
    """Модель пользователя Фудграм."""
    avatar = models.ImageField(
        upload_to='users/avatars/',
        blank=True
    )
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    @property
    def is_subscribed(self):
        """Возвращает True, если пользователь подписан на этого автора."""
        return self.subscribtions.filter(subscribing=self).exists()


class Subscribe(models.Model):
    """Модель подписки на пользователя."""
    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Пользователь'
    )
    subscribing = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='subscribtions',
        verbose_name='Подписка на'
    )

    class Meta:
        verbose_name = 'Подписка на'
        verbose_name_plural = 'Подписки'
        unique_together = ('user', 'subscribing')

    def __str__(self):
        return self.subscribing.username
