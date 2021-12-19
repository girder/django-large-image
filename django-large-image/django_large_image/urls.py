from django.urls import path, register_converter
from django_large_image import rest, views
from rest_framework.routers import SimpleRouter

router = SimpleRouter(trailing_slash=False)
router.register(r'api/large_image/image_set', rest.viewsets.ImageSetViewSet)
router.register(r'api/large_image', rest.viewsets.ImageViewSet, basename='imagery')


class FloatUrlParameterConverter:
    regex = r'-?[0-9]+\.?[0-9]+'

    def to_python(self, value):
        return float(value)

    def to_url(self, value):
        return str(value)


register_converter(FloatUrlParameterConverter, 'float')


urlpatterns = [
    path('large_image/<int:pk>/', views.ImageDetailView.as_view(), name='image-detail'),
    path(
        'api/large_image/<int:pk>/tiles',
        rest.tiles.TileMetadataView.as_view(),
        name='image-tile-metadata',
    ),
    path(
        'api/large_image/<int:pk>/tiles/internal',
        rest.tiles.TileInternalMetadataView.as_view(),
        name='image-tile-internal-metadata',
    ),
    path(
        'api/large_image/<int:pk>/tiles/<int:z>/<int:x>/<int:y>.png',
        rest.tiles.TileView.as_view(),
        name='image-tiles',
    ),
    path(
        'api/large_image/<int:pk>/tiles/region/<float:left>/<float:right>/<float:bottom>/<float:top>/region.tif',
        rest.tiles.TileRegionView.as_view(),
        name='image-region',
    ),
    path(
        'api/large_image/<int:pk>/tiles/<int:z>/<int:x>/<int:y>/corners',
        rest.tiles.TileCornersView.as_view(),
        name='image-tile-corners',
    ),
    path(
        'api/large_image/<int:pk>/tiles/thumbnail',
        rest.tiles.TileThumnailView.as_view(),
        name='image-thumbnail',
    ),
    path(
        'api/large_image/<int:pk>/tiles/bands',
        rest.tiles.TileBandInfoView.as_view(),
        name='image-bands',
    ),
    path(
        'api/large_image/<int:pk>/tiles/bands/<int:band>',
        rest.tiles.TileSingleBandInfoView.as_view(),
        name='image-bands-single',
    ),
    path(
        'api/large_image/<int:pk>/tiles/pixel/<int:left>/<int:top>',
        rest.tiles.TilePixelView.as_view(),
        name='image-pixel',
    ),
    path(
        'api/large_image/<int:pk>/tiles/histogram',
        rest.tiles.TileHistogramView.as_view(),
        name='image-histogram',
    ),
    path(
        'api/large_image/sources',
        rest.tiles.ListTileSourcesView.as_view(),
        name='large-image-sources',
    ),
] + router.urls
