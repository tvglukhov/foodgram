from django.contrib.auth.models import AbstractUser
from django.db import models


class FoodgramUser(AbstractUser):
    """Модель пользователя Фудграм."""
    avatar = models.URLField(blank=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    @property
    def is_subscribed(self):
        """Возвращает True, если пользователь подписан на этого автора."""
        return self.subscribers.filter(subscribing=self).exists()


class Subscribe(models.Model):
    """Модель подписки на пользователя."""
    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )
    subscribing = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='subscribtions'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ('user', 'subscribing')
