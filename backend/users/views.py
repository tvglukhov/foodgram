from django.contrib.auth import get_user_model
from rest_framework import mixins, status, viewsets
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


from .serializers import (ChangePasswordSerializer,
                          UserSerializer,
                          UserCreateSerializer,
                          UserAvatarSerializer,)

User = get_user_model()


class UsersViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    """Вьюсет модели пользователя."""
    queryset = User.objects.all().order_by('username')
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        """Выбор класса в зависимости от запроса."""
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer


class UserSelfView(mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    """Класс обработки запросов пользователя к своему профилю."""
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user


class UserAvatarViewSet(mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    """Класс обновления и удаления аватара Пользователя."""

    def update(self, request, *args, **kwargs):
        user = request.user
        serializer = UserAvatarSerializer(instance=user,
                                          data=request.data)

        if serializer.is_valid():
            return Response(
                'Аватар успешно добавлен',
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request):
        user = request.user
        serializer = UserAvatarSerializer(instance=user)
        serializer.delete_avatar(user)
        return Response(
            'Аватар успешно удалён',
            status=status.HTTP_204_NO_CONTENT
        )


class UpdatePasswordView(CreateAPIView):
    """Обработка запроса на изменение пароля."""
    serializer_class = ChangePasswordSerializer
    queryset = User.objects.all()
    http_method_names = ['create']

    def get_object(self):
        return self.request.user
