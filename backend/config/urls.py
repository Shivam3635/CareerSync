from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/profile/', include('students.urls')),
    path('api/jobs/', include('jobs.urls')),
    path('api/admin/', include('jobs.admin_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
