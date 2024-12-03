from django.urls import include, path

from . import views

app_name = 'users'

urlpatterns = [
    # path(
    #     'users/',
    #     views.UsersViewSet.as_view({'get': 'list', 'post': 'create'}),
    #     name='users'
    # ),
    # path(
    #     'users/<int:pk>/',
    #     views.UsersViewSet.as_view({'get': 'retrieve'}),
    #     name='user-detail'
    # ),
    # path(
    #     'users/me/',
    #     views.UserSelfView.as_view({'get': 'retrieve'}),
    #     name='user-me'
    # ),
    # path(
    #     'users/me/avatar/',
    #     views.UserAvatarViewSet.as_view({'put': 'update',
    #                                      'delete': 'destroy'}),
    #     name='user-avatar'
    # ),
    # path(
    #     'users/set_password/',
    #     views.UpdatePasswordView.as_view(),
    #     name='user-set-password'
    # ),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
