from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg.utils import swagger_auto_schema
from large_image.exceptions import TileSourceXYZRangeError
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from django_large_image.rest import params
from django_large_image.rest.base import CACHE_TIMEOUT, BaseLargeImageView


class Tiles(BaseLargeImageView):
    @method_decorator(cache_page(CACHE_TIMEOUT))
    @swagger_auto_schema(
        method='GET',
        operation_summary='Returns tile image.',
        manual_parameters=[params.projection, params.z, params.x, params.y] + params.STYLE,
    )
    @action(detail=True, url_path=r'tiles/(?P<z>\w+)/(?P<x>\w+)/(?P<y>\w+).png')
    def tile(self, request: Request, pk: int, x: int, y: int, z: int) -> HttpResponse:
        source = self.get_tile_source(request, pk)
        try:
            tile_binary = source.getTile(int(x), int(y), int(z))
        except TileSourceXYZRangeError as e:
            raise ValidationError(e)
        mime_type = source.getTileMimeType()
        return HttpResponse(tile_binary, content_type=mime_type)

    @swagger_auto_schema(
        method='GET',
        operation_summary='Returns bounds of a tile for a given x, y, z index.',
        manual_parameters=[params.projection, params.z, params.x, params.y],
    )
    @action(
        detail=True, methods=['get'], url_path=r'tiles/(?P<z>\w+)/(?P<x>\w+)/(?P<y>\w+)/corners'
    )
    def tile_corners(self, request: Request, pk: int, x: int, y: int, z: int) -> HttpResponse:
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
