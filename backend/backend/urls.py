from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from api import urls as api_urls

from api.views import RedirectShortLinkView


urlpatterns = [
    path('s/<str:short_link>/', RedirectShortLinkView.as_view()),
    path('admin/', admin.site.urls),
    path('api/', include(api_urls)),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
