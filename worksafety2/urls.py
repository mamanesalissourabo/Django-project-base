
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path("", include("base.urls")),
    path("incident", include("incident.urls")),
    path("planaction", include("planaction.urls")),
    path("faq", include("faq.urls")),
    path("reward", include("reward.urls")),
    path("dashboard", include("dashboard.urls")),
    path('admin/', admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path('api-auth/', include('rest_framework.urls'))
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

