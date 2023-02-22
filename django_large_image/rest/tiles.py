from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from large_image.exceptions import TileSourceXYZRangeError
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from django_large_image import tilesource
from django_large_image.rest import params
from django_large_image.rest.base import LargeImageMixinBase
from django_large_image.rest.renderers import image_renderers
from django_large_image.rest.serializers import TileMetadataSerializer

tile_metadata_summary = 'Returns tile metadata.'
tile_metadata_parameters = params.BASE
tile_summary = 'Returns tile image binary.'
tile_parameters = params.BASE + [params.z, params.x, params.y, params.fmt_png] + params.STYLE
tile_corners_summary = 'Returns bounds of a tile for a given x, y, z index.'
tile_corners_parameters = params.BASE + [params.z, params.x, params.y]


class TilesMixin(LargeImageMixinBase):
    @extend_schema(
        methods=['GET'],
        summary=tile_metadata_summary,
        parameters=tile_metadata_parameters,
    )
    @action(detail=False, url_path=r'tiles/metadata')
    def tiles_metadata(self, request: Request, pk: int = None, **kwargs) -> Response:
        source = self.get_tile_source(request, pk, style=False)
        source.dli_geospatial = tilesource.is_geospatial(source)
        serializer = TileMetadataSerializer(source)
        return Response(serializer.data)

    @extend_schema(
        methods=['GET'],
        summary=tile_summary,
        parameters=tile_parameters,
    )
    @action(
        detail=False,
        url_path=rf'tiles/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+).{params.FORMAT_URL_PATTERN}',
        renderer_classes=image_renderers,
    )
    def tile(
        self, request: Request, x: int, y: int, z: int, pk: int = None, fmt: str = 'png', **kwargs
    ) -> HttpResponse:
        encoding = tilesource.format_to_encoding(fmt, pil_safe=True)
        source = self.get_tile_source(request, pk, encoding=encoding)
        try:
            tile_binary = source.getTile(int(x), int(y), int(z))
        except TileSourceXYZRangeError as e:
            raise ValidationError(e)
        mime_type = source.getTileMimeType()
        return HttpResponse(tile_binary, content_type=mime_type)

    @extend_schema(
        methods=['GET'],
        summary=tile_corners_summary,
        parameters=tile_corners_parameters,
    )
    @action(
        detail=False, methods=['get'], url_path=r'tiles/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+)/corners'
    )
    def tile_corners(
        self, request: Request, x: int, y: int, z: int, pk: int = None, **kwargs
    ) -> HttpResponse:
        source = self.get_tile_source(request, pk, style=False)
        xmin, ymin, xmax, ymax = source.getTileCorners(int(z), int(x), int(y))
        metadata = {
            'xmin': xmin,
            'xmax': xmax,
            'ymin': ymin,
            'ymax': ymax,
            'proj4': source.getProj4String(),
        }
        return Response(metadata)


class TilesDetailMixin(TilesMixin):
    @extend_schema(
        methods=['GET'],
        summary=tile_metadata_summary,
        parameters=tile_metadata_parameters,
    )
    @action(detail=True, url_path=r'tiles/metadata')
    def tiles_metadata(self, request: Request, pk: int = None, **kwargs) -> Response:
        return super().tiles_metadata(request, pk)

    @extend_schema(
        methods=['GET'],
        summary=tile_summary,
        parameters=tile_parameters,
    )
    @action(
        detail=True,
        url_path=rf'tiles/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+).{params.FORMAT_URL_PATTERN}',
        renderer_classes=image_renderers,
    )
    def tile(
        self, request: Request, x: int, y: int, z: int, pk: int = None, fmt: str = 'png', **kwargs
    ) -> HttpResponse:
        return super().tile(request, x, y, z, pk, fmt)

    @extend_schema(
        methods=['GET'],
        summary=tile_corners_summary,
        parameters=tile_corners_parameters,
    )
    @action(
        detail=True, methods=['get'], url_path=r'tiles/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+)/corners'
    )
    def tile_corners(
        self, request: Request, x: int, y: int, z: int, pk: int = None, **kwargs
    ) -> HttpResponse:
        return super().tile_corners(request, x, y, z, pk)
