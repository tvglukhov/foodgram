from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views


app_name = 'recipes'

router = SimpleRouter()
router.register('recipes', views.RecipeViewSet, basename='recipes')
router.register('ingredients',
                views.IngridientsViewSet,
                basename='ingredients')
router.register('tags', views.TagsViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
]
