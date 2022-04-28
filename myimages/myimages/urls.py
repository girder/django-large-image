"""myimages URL Configuration.

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
from django.urls import include, path, re_path
from django.views.generic.base import RedirectView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import SimpleRouter

from myimages.imagefiles.viewsets import ImageFileDetailViewSet

router = SimpleRouter(trailing_slash=False)
router.register(r'api/imagefile', ImageFileDetailViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('django_large_image.urls')),
    path(r'', RedirectView.as_view(url='admin/', permanent=False), name='index'),
] + router.urls

schema_view = get_schema_view(
    openapi.Info(
        title='Resonant GeoData API',
        default_version='v1',
        description='Resonant GeoData',
        # terms_of_service='https://www.google.com/policies/terms/',
        contact=openapi.Contact(email='kitware@kitare.com'),
        license=openapi.License(name='Apache 2.0'),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=urlpatterns,
)

urlpatterns += [
    re_path(
        r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json',
    ),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
