from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import SimpleRouter

from users import urls as users_urls


app_name = 'api'

# router = SimpleRouter()
# router.register


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/', include(router.urls)),
    path('api/', include(users_urls))
]

# if settings.DEBUG:
#     urlpatterns += static(
#         settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
#     )
#     urlpatterns += static(
#         settings.STATIC_URL, document_root=settings.STATIC_ROOT
#     )
