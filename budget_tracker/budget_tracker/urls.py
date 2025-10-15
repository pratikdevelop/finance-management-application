"""
URL configuration for budget_tracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token

# Health check view
def health_check(request):
    return HttpResponse("✅ Budget Tracker API is running!")

# Debug info view
def debug_info(request):
    import os
    info = {
        "status": "running",
        "debug": settings.DEBUG,
        "allowed_hosts": settings.ALLOWED_HOSTS,
        "database_engine": settings.DATABASES['default']['ENGINE'],
    }
    from django.http import JsonResponse
    return JsonResponse(info)

urlpatterns = [
    # Root and health endpoints
    path('', health_check, name='home'),
    path('health/', health_check, name='health'),
    path('debug/', debug_info, name='debug'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('budget.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)