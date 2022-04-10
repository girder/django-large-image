from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg.utils import swagger_auto_schema
from large_image.exceptions import TileSourceXYZRangeError
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from django_large_image import tilesource
from django_large_image.rest import params
from django_large_image.rest.base import CACHE_TIMEOUT, LargeImageMixinBase

tile_summary = 'Returns tile image binary.'
tile_parameters = [params.projection, params.z, params.x, params.y] + params.STYLE
tile_corners_summary = 'Returns bounds of a tile for a given x, y, z index.'
tile_corners_parameters = [params.projection, params.z, params.x, params.y]


class TilesMixin(LargeImageMixinBase):
    def tile(
        self, request: Request, x: int, y: int, z: int, pk: int = None, format: str = None
    ) -> HttpResponse:
        encoding = tilesource.format_to_encoding(format)
        source = self.get_tile_source(request, pk, encoding=encoding)
        try:
            tile_binary = source.getTile(int(x), int(y), int(z), encoding=encoding)
        except TileSourceXYZRangeError as e:
            raise ValidationError(e)
        mime_type = source.getTileMimeType()
        return HttpResponse(tile_binary, content_type=mime_type)

    @method_decorator(cache_page(CACHE_TIMEOUT))
    @swagger_auto_schema(
        method='GET',
        operation_summary=tile_summary,
        manual_parameters=tile_parameters,
    )
    @action(detail=False, url_path=r'tiles/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+).png')
    def tile_png(
        self,
        request: Request,
        x: int,
        y: int,
        z: int,
        pk: int = None,
    ) -> HttpResponse:
        return self.tile(request, x, y, z, pk=pk, format='png')

    @method_decorator(cache_page(CACHE_TIMEOUT))
    @swagger_auto_schema(
        method='GET',
        operation_summary=tile_summary,
        manual_parameters=tile_parameters,
    )
    @action(detail=False, url_path=r'tiles/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+).jpeg')
    def tile_jpeg(
        self,
        request: Request,
        x: int,
        y: int,
        z: int,
        pk: int = None,
    ) -> HttpResponse:
        return self.tile(request, x, y, z, pk=pk, format='jpeg')

    @swagger_auto_schema(
        method='GET',
        operation_summary=tile_corners_summary,
        manual_parameters=tile_corners_parameters,
    )
    @action(
        detail=False, methods=['get'], url_path=r'tiles/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+)/corners'
    )
    def tile_corners(
        self, request: Request, x: int, y: int, z: int, pk: int = None
    ) -> HttpResponse:
        source = self.get_tile_source(request, pk)
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
    @swagger_auto_schema(
        method='GET',
        operation_summary=tile_summary,
        manual_parameters=tile_parameters,
    )
    @action(detail=True, url_path=r'tiles/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+).png')
    def tile_png(
        self,
        request: Request,
        x: int,
        y: int,
        z: int,
        pk: int = None,
    ) -> HttpResponse:
        return super().tile_png(request, x, y, z, pk)

    @swagger_auto_schema(
        method='GET',
        operation_summary=tile_summary,
        manual_parameters=tile_parameters,
    )
    @action(detail=True, url_path=r'tiles/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+).jpeg')
    def tile_jpeg(
        self,
        request: Request,
        x: int,
        y: int,
        z: int,
        pk: int = None,
    ) -> HttpResponse:
        return super().tile_jpeg(request, x, y, z, pk)

    @swagger_auto_schema(
        method='GET',
        operation_summary=tile_corners_summary,
        manual_parameters=tile_corners_parameters,
    )
    @action(
        detail=True, methods=['get'], url_path=r'tiles/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+)/corners'
    )
    def tile_corners(
        self, request: Request, x: int, y: int, z: int, pk: int = None
    ) -> HttpResponse:
        return super().tile_corners(request, x, y, z, pk)
