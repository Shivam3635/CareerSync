from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path('health/', health_check, name='health'),
    path('api/health/', health_check, name='api_health'),
    path('django-admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/profile/', include('students.urls')),
    path('api/jobs/', include('jobs.urls')),
    path('api/admin/', include('jobs.admin_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
