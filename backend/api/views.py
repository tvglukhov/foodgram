from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import FirstLetterFilter, RecipeFilter
from .paginations import PageLimitPagination
from .permissions import AllowAnyExceptEndpointMe, AuthorOrReadOnly
from .serializers import (AddRecipeSerializer,
                          IngredientSerializer,
                          RecipeSerializer,
                          SubscribeUserSerializer,
                          TagSerializer,
                          UserAvatarSerializer,)
from users.models import Subscribe
from recipes.models import (Favorite,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            Tag,
                            ShoppingCart,
                            ShortLinkRecipe,)

User = get_user_model()


class FoodgramUserViewSet(UserViewSet):
    """Кастомизация стандартного вьюсета модели Юзера."""
    permission_classes = (AllowAnyExceptEndpointMe,)

    @action(
        detail=True,
        url_path='subscribe',
        methods=('POST', 'DELETE'),
        permission_classes=(IsAuthenticated,)
    )
    def subcribe_or_unsubscribe(self, request, id):
        """Подписка / отмена подписки на пользователя."""
        author = get_object_or_404(User, id=id)
        user = request.user

        if request.method == 'POST':
            serializer = SubscribeUserSerializer(
                author,
                data={'user': user},
                context={'request': request,
                         'author': author}
            )
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=user, subscribing=author)
            return Response(data=serializer.data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            try:
                subscription = user.subscribers.get(subscribing=author)
            except Subscribe.DoesNotExist:
                return Response({'Ошибка': 'Подписка не найдена.'},
                                status=status.HTTP_400_BAD_REQUEST)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class UserAvatarViewSet(mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    """Класс обновления и удаления аватара Пользователя."""
    serializer_class = UserAvatarSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def destroy(self, request):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        serializer.delete_avatar(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetSubscribersViewSet(mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """Вью для получения списка пользователей."""
    serializer_class = SubscribeUserSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return User.objects.filter(subscribtions__user=self.request.user)


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


class IngridientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет запросов к Ингридиентам."""
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter, FirstLetterFilter)
    search_fields = ('name',)

    def get_queryset(self):
        if 'pk' in self.kwargs:
            return Ingredient.objects.filter(pk=self.kwargs['pk'])
        return Ingredient.objects.all()


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет запросов к Ингридиентам."""
    serializer_class = TagSerializer
    pagination_class = None

    def get_queryset(self):
        if 'pk' in self.kwargs:
            return Tag.objects.filter(pk=self.kwargs['pk'])
        return Tag.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет запросов к Рецептам."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnly,)
    pagination_class = PageLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        """Автор переопределяется текущим Пользователем."""
        serializer.save(author=self.request.user)

    def add_recipe(self, model, request, pk=None):
        """Добавление Рецепта."""
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = AddRecipeSerializer(
            recipe,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        if model.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(user=request.user, recipe=recipe)
        modified_data = {
            **serializer.data,
            'image': request.build_absolute_uri(
                recipe.image.url
            )
        }
        return Response(modified_data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, model, request, pk=None):
        """Удаление Рецепта."""
        recipe = get_object_or_404(Recipe, id=pk)
        shopping_cart_item = model.objects.filter(
            user=request.user,
            recipe=recipe
        ).first()
        if not shopping_cart_item:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        shopping_cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        url_path='shopping_cart',
        methods=('post', 'delete'),
        permission_classes=(AuthorOrReadOnly,)
    )
    def add_delete_shopping_cart(self, request, pk):
        """Добавление и удаление Рецепта из Списка покупок."""
        if request.method == 'POST':
            return self.add_recipe(ShoppingCart, request, pk)
        if request.method == 'DELETE':
            return self.delete_recipe(ShoppingCart, request, pk)

    @action(
        detail=True,
        url_path='favorite',
        methods=('post', 'delete'),
        permission_classes=(AuthorOrReadOnly,)
    )
    def add_delete_favorite(self, request, pk):
        """Добавление и удаление Рецепта из Избранного."""
        if request.method == 'POST':
            return self.add_recipe(Favorite, request, pk)
        if request.method == 'DELETE':
            return self.delete_recipe(Favorite, request, pk)

    @action(
        detail=False,
        url_path='download_shopping_cart',
        methods=('get',),
        permission_classes=(AuthorOrReadOnly,)
    )
    def download_shopping_cart(self, request):
        """Скачать корзинку."""
        ingredients_in_cart = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(
            amount=Sum('amount')
        ).order_by(
            'ingredient__name'
        )
        print(ingredients_in_cart)

        shopping_list = {}
        for item in ingredients_in_cart:
            shopping_list[item['ingredient__name']] = (
                f'{item["amount"]} '
                f'{item["ingredient__measurement_unit"]}'
            )

        content = '\n'.join(
            [f"{key}: {value}" for key, value in shopping_list.items()]
        )

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="Список_покупок.txt"'
        )
        return response

    @action(
        detail=True,
        url_path='get-link',
        methods=('get',),
    )
    def get_direct_link(self, request, pk):
        """Возвращает прямую ссылку на Рецепт."""
        short_link = get_object_or_404(
            ShortLinkRecipe,
            recipe_id=pk
        )
        return JsonResponse(
            {"short-link": request.build_absolute_uri(
                f'/s/{short_link.short_link_code}/'
            )}
        )
