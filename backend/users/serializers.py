import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, status
from rest_framework.exceptions import APIException

from .models import Subscribe
from recipes.models import Recipe
from recipes.serializers import AddRecipeSerializer


User = get_user_model()


class BadRequest(APIException):
    """Возвращает статус-код 400."""
    default_detail = '400 Bad Request'
    default_code = 'bad_request'
    status_code = status.HTTP_400_BAD_REQUEST


class UserCreationSerializer(UserCreateSerializer):
    """Кастомизация сериализатора регистрации пользователя."""
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)


class FoodgramUserSerializer(UserSerializer):
    """Кастомизация сериализатора модели Пользователя."""
    is_subscribed = serializers.BooleanField(read_only=True)
    avatar = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'avatar')

    def get_avatar(self, obj):
        """Возвращает абсолютную ссылку на аватар."""
        request = self.context.get('request')
        if obj.avatar:
            return request.build_absolute_uri(obj.avatar.url)
        return None


class Base64ImageField(serializers.ImageField):
    """Создание поля для декодирования изображения формата base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор запросов на обновление и удаление Аватара."""
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)

    def update(self, instance, validated_data):
        if 'avatar' in validated_data:
            instance.avatar = validated_data['avatar']
            instance.save()
        return instance

    def delete_avatar(self, instance):
        """Удаление аватара."""
        instance.avatar.delete()
        instance.avatar = None
        instance.save()


class SubscribeUserSerializer(FoodgramUserSerializer):
    """Сериализатор запросов на подписку на автора."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar',
                  'recipes', 'recipes_count')
        read_only_fields = ('id', 'email', 'username', 'first_name',
                            'last_name', 'is_subscribed', 'avatar',
                            'recipes', 'recipes_count')

    def validate(self, data):
        """Валидация запроса на подписку."""
        author = self.context.get('author')
        user = self.context.get('request').user
        if user == author:
            raise BadRequest
        if Subscribe.objects.filter(user=user, subscribing=author).exists():
            raise BadRequest
        return data

    def get_author_recipes(self, author):
        """Выборка рецептов Автора."""
        return Recipe.objects.filter(author=author)

    def get_recipes(self, author):
        """Получение списка рецептов Пользователя."""
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')

        if recipes_limit:
            recipes_limit = int(recipes_limit)
        recipes = self.get_author_recipes(author)[:recipes_limit]

        return AddRecipeSerializer(
            recipes,
            many=True,
            context={'request': request},
        ).data

    def get_recipes_count(self, author):
        """Подсчет количества рецептов Автора."""
        return self.get_author_recipes(author).count()
