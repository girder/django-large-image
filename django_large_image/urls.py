from django.urls import path, register_converter

from django_large_image import rest


class FloatUrlParameterConverter:
    regex = r'-?[0-9]+\.?[0-9]+'

    def to_python(self, value):
        return float(value)

    def to_url(self, value):
        return str(value)


register_converter(FloatUrlParameterConverter, 'float')


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
