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
from django.urls import include, path
from django.views.generic.base import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from myimages.imagefiles.viewsets import ImageFileDetailViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter(trailing_slash=False)
router.register(r'api/imagefile', ImageFileDetailViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('django_large_image.urls')),
    path(r'', RedirectView.as_view(url='admin/', permanent=False), name='index'),
] + router.urls


urlpatterns += [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(), name='schema-swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(), name='schema-redoc'),
]
