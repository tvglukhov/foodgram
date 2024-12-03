import base64
import re

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.core.files.base import ContentFile
from rest_framework import serializers

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания нового пользователя."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'password'
        )

    def validate(self, data):
        """Валидация запроса на регистрацию пользователя."""

        required_fields = [
            'username', 'email', 'first_name', 'last_name', 'password'
        ]
        for field in required_fields:
            if field not in data:
                raise serializers.ValidationError(
                    f'Поле {field} не может быть пустым!'
                )

        if not re.match(r'^[\w.@+-]+\Z', data['username']):
            raise serializers.ValidationError(
                'В поле username могут быть использованы цифры, буквы, ',
                'нижнее подчеркивание, знаки минуса или плюса.'
            )

        if data['username'] == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать "me" в качестве имени!'
            )

        user_email = User.objects.filter(email=data['email']).first()
        user_username = User.objects.filter(username=data['username']).first()

        if user_email and user_email.username != data['username']:
            raise serializers.ValidationError(
                'Пользователь с таким email уже зарегестрирован!'
            )

        if user_username and user_username.email != data['email']:
            raise serializers.ValidationError(
                'Пользователь с таким именем уже зарегестрирован!'
            )

        data['password'] = make_password(data['password'])

        return data

    def to_representation(self, instance):
        return {
            "email": instance.email,
            "id": instance.id,
            "username": instance.username,
            "first_name": instance.first_name,
            "last_name": instance.last_name
        }


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор GET запросов к модели пользователя."""
    is_subscribed = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'avatar',
            'is_subscribed'
        )
        ordering = ('username')

    def get_is_subscribed(self, obj):
        """Получение состояния Подписки на автора."""
        return obj.is_subscribed


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

    def validate(self, data):
        """Валидация запроса на обновление Аватара."""
        if 'avatar' not in data:
            raise serializers.ValidationError(
                'Изображение не загружено.'
            )

        return data

    def to_representation(self, instance):
        """Замена base64 кода на абсолютную ссылку в данных Аватара."""
        data = super().to_representation(instance)
        if instance.avatar:
            data['avatar'] = instance.avatar.url
        return data

    def delete_avatar(self, instance):
        """Удаление аватара."""
        instance.avatar.delete()
        instance.avatar = None
        instance.save()


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор запроса на изменение пароля."""
    new_password = serializers.CharField()
    current_password = serializers.CharField()

    def get_user(self):
        """Извлечение объекта пользователя."""
        return self.context['request'].user

    def validate(self, data):
        """Валидация запроса на изменение пароля."""

        if not check_password(data['current_password'],
                              self.get_user().password):
            raise serializers.ValidationError(
                'Пароль указан неверно.'
            )

        return data

    def save(self):
        """Сохранение нового пароля."""
        user = self.get_user()
        user.set_password(self.validated_data['new_password'])
        user.save()
