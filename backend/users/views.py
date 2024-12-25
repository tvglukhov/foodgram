from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subscribe
from .permissions import AllowAnyExceptEndpointMe
from .serializers import (UserAvatarSerializer,
                          SubscribeUserSerializer)

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
            subscription = Subscribe.objects.filter(
                user=user,
                subscribing=author
            ).first()
            if not subscription:
                return Response(status=status.HTTP_400_BAD_REQUEST)
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
