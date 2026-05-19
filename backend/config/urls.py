from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('django-admin/', admin.site.urls),

    path('api/auth/', include('apps.users.urls')),
    path('api/', include('apps.articles.urls')),
    path('api/', include('apps.comments.urls')),
    path('api/', include('apps.moderation.urls')),
    path('api/', include('apps.newsletter.urls')),
    path('api/', include('apps.audit.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
