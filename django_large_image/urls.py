from django.urls import path

from django_large_image import rest

urlpatterns = [
    path(
        'api/large-image/sources',
        rest.ListTileSourcesView.as_view(),
        name='large-image-sources',
    ),
    path(
        'api/large-image/colormaps',
        rest.ListColormapsView.as_view(),
        name='large-image-colormaps',
    ),
]
