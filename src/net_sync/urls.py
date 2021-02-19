"""net_sync URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from rest_framework.documentation import include_docs_urls
from .views import BlackListTokenView as _bltv

from rest_framework_simplejwt.views import (
    TokenObtainPairView as _topv,
    TokenRefreshView as _trv,
)

urlpatterns = [
    path('api/v2.0/auth/login/', _topv.as_view(), name='token_obtain_pair'),
    path('api/v2.0/auth/refresh/', _trv.as_view(), name='token_refresh'),
    path('api/v2.0/auth/logout/', _bltv.as_view(), name='token_blacklist'),
    path('admin/', admin.site.urls),
    path('api/', include('apps.api.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', include('apps.frontend.urls')),
    path('docs/', include_docs_urls(title='NetSyncAPI')),
]
