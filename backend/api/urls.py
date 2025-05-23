from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views


app_name = 'api'

router = SimpleRouter()
router.register(r'users', views.FoodgramUserViewSet)
router.register(r'recipes', views.RecipeViewSet, basename='recipes')
router.register(r'ingredients',
                views.IngridientsViewSet,
                basename='ingredients')
router.register(r'tags', views.TagsViewSet, basename='tags')

urlpatterns = [
    path(
        'users/me/avatar/', views.UserAvatarViewSet.as_view({
            'put': 'update',
            'delete': 'destroy'
        })
    ),
    path(
        'users/subscriptions/', views.GetSubscribersViewSet.as_view({
            'get': 'list'
        })
    ),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
