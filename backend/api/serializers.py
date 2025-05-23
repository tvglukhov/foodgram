import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .constants import (INTEGER_FIELD_MAX_VALUE,
                        INTEGER_FIELD_MIN_VALUE,
                        CHAR_FIELD_MAX_LENGTH)
from recipes.models import (Ingredient,
                            Favorite,
                            Recipe,
                            RecipeIngredient,
                            Tag,
                            ShoppingCart)

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для изображений в base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserCreationSerializer(UserCreateSerializer):
    """Кастомизация сериализатора регистрации пользователя."""
    first_name = serializers.CharField(max_length=CHAR_FIELD_MAX_LENGTH)
    last_name = serializers.CharField(max_length=CHAR_FIELD_MAX_LENGTH)


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
        author = self.context['author']
        user = self.context['request'].user

        if user == author:
            raise ValidationError('Нельзя подписаться на самого себя.')

        if user.subscribers.filter(subscribing=author).exists():
            raise ValidationError('Нельзя подписаться на пользователя дважды.')

        return data

    def get_recipes(self, author):
        """Получение списка рецептов Пользователя."""
        request = self.context['request']
        recipes_limit = request.query_params.get('recipes_limit')

        if recipes_limit:
            recipes_limit = int(recipes_limit)
        recipes = author.recipes.all()[:recipes_limit]

        return AddRecipeSerializer(
            recipes,
            many=True,
            context={'request': request},
        ).data

    def get_recipes_count(self, author):
        """Подсчет количества рецептов Автора."""
        return author.recipes.all().count()


class AuthorSerializer(serializers.ModelSerializer):
    """Сериализатор запросов к Автору контента."""

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'avatar')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор запросов к Ингридиентам."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор запросов к Тэгам."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для записи ингредиентов в рецепт."""
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )
    amount = serializers.IntegerField(
        min_value=INTEGER_FIELD_MIN_VALUE,
        max_value=INTEGER_FIELD_MAX_VALUE
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'amount', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='recipe_ingredient')
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    cooking_time = serializers.IntegerField(
        min_value=INTEGER_FIELD_MIN_VALUE,
        max_value=INTEGER_FIELD_MAX_VALUE
    )
    image = Base64ImageField()
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'text', 'image', 'cooking_time', 'tags',
            'ingredients', 'author', 'is_in_shopping_cart', 'is_favorited'
        )
        read_only_fields = ('author',)

    def validate(self, data):
        """Валидация запроса на создание Рецепта."""
        ingredients = data.get('recipe_ingredient')
        tags = data.get('tags')

        if not ingredients:
            raise ValidationError('Нельзя создать рецепт без ингредиентов.')

        if not tags:
            raise ValidationError('Нельзя создать рецепт без тэгов.')

        ingredient_ids = [ingredient['ingredient']['id']
                          for ingredient in ingredients]
        tag_ids = [tag.id for tag in tags]

        if (not Ingredient.objects.filter(id__in=ingredient_ids).count()
                == len(ingredient_ids)):
            raise ValidationError('Указаны несуществующие ингредиенты.')

        if (not Tag.objects.filter(id__in=tag_ids).count()
                == len(tag_ids)):
            raise ValidationError('Указаны несуществующие тэги.')

        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise ValidationError('Такой ингредиент уже есть в рецепте.')

        if len(tag_ids) != len(set(tag_ids)):
            raise ValidationError('Такой тэг уже присвоен рецепту.')

        return data

    def is_recipe_in(self, model, recipe):
        """Возвращает True, если рецепт добавлен в модель."""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return model.objects.filter(recipe=recipe,
                                    user=user).exists()

    def get_is_in_shopping_cart(self, recipe):
        """Возвращает True, если рецепт добавлен в Список покупок."""
        return self.is_recipe_in(ShoppingCart, recipe)

    def get_is_favorited(self, recipe):
        """Возвращает True, если рецепт добавлен в Избранное."""
        return self.is_recipe_in(Favorite, recipe)

    def create_ingredients(self, ingredients, recipe):
        """Создание списка Ингредиентов в рецепте."""
        recipe_ingredients = []

        for ingredient_data in ingredients:
            ingredient_id = ingredient_data['ingredient']['id']
            ingredient = Ingredient.objects.get(id=ingredient_id)
            amount = ingredient_data['amount']
            recipe_ingredients.append(RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            ))

        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        """Переопределение метода для обработки Тэгов и Ингредиентов."""
        ingredients = validated_data.pop('recipe_ingredient')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        self.create_ingredients(ingredients, recipe)

        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        """Редактирование рецепта."""
        recipe = instance
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredient')
        RecipeIngredient.objects.filter(recipe=recipe).delete()

        self.create_ingredients(
            ingredients,
            recipe
        )

        updated_instance = super().update(instance, validated_data)
        updated_instance.tags.set(tags)

        return updated_instance

    def to_representation(self, instance):
        """Переопределение вывода Тэгов при создании рецепта."""
        representation = super().to_representation(instance)
        tags_data = [{'id': tag.id, 'name': tag.name, 'slug': tag.slug}
                     for tag in instance.tags.all()]
        representation['tags'] = tags_data
        return representation


class AddRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор запросов к модели Списка покупок и избранного."""
    image = serializers.SerializerMethodField()
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)

    def get_image(self, obj):
        """Возвращает абсолютную ссылку на изображение."""
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None
