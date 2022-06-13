"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView)
from clicoh.urls import router as clicoh_router
from rest_framework.schemas import get_schema_view
from rest_framework import urls as restframework_urls
from rest_framework.renderers import JSONOpenAPIRenderer
from rest_framework.permissions import IsAuthenticated


schema_view = get_schema_view(
    title="The Clicoh' things",
    renderer_classes=[JSONOpenAPIRenderer],
    permission_classes=[],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('schema.json', schema_view, name="schema-json"),
    path('swagger-ui/', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url': 'schema-json'}
    ), name='swagger-ui'),
    path('auth/', include(restframework_urls, namespace="rest_framework")),
    path('api/token/', TokenObtainPairView.as_view(), name='api-jwt-auth'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include('clicoh.urls')),
]
