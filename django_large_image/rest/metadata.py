from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from django_large_image import utilities
from django_large_image.rest.core import CACHE_TIMEOUT, BaseLargeImageView
from django_large_image.rest.params import band_param


class MetaData(BaseLargeImageView):
    @swagger_auto_schema(
        method='GET',
        operation_summary='Returns tile metadata.',
    )
    @action(detail=True)
    def metadata(self, request: Request, pk: int) -> Response:
        tile_source = self._get_tile_source(request, pk)
        metadata = tile_source.getMetadata()
        metadata.setdefault('geospatial', False)
        if metadata['geospatial']:
            bounds = utilities.get_tile_bounds(tile_source)
            metadata['bounds'] = bounds
        return Response(metadata)

    """Returns additional known metadata about the tile source."""

    @swagger_auto_schema(
        method='GET',
        operation_summary='Returns additional known metadata about the tile source.',
    )
    @action(detail=True)
    def internal_metadata(self, request: Request, pk: int) -> Response:
        tile_source = self._get_tile_source(request, pk)
        metadata = tile_source.getInternalMetadata()
        metadata.setdefault('geospatial', False)
        if metadata['geospatial']:
            bounds = utilities.get_tile_bounds(tile_source)
            metadata['bounds'] = bounds
        return Response(metadata)

    @method_decorator(cache_page(CACHE_TIMEOUT))
    @swagger_auto_schema(
        method='GET',
        operation_summary='Returns thumbnail of full image.',
    )
    @action(detail=True)
    def thumbnail(self, request: Request, pk: int) -> HttpResponse:
        tile_source = self._get_tile_source(request, pk)
        thumb_data, mime_type = tile_source.getThumbnail(encoding='PNG')
        return HttpResponse(thumb_data, content_type=mime_type)

    @swagger_auto_schema(
        method='GET',
        operation_summary='Returns bands information.',
    )
    @action(detail=True)
    def bands(self, request: Request, pk: int) -> Response:
        tile_source = self._get_tile_source(request, pk)
        metadata = tile_source.getBandInformation()
        return Response(metadata)

    @swagger_auto_schema(
        method='GET',
        operation_summary='Returns single band information.',
        manual_parameters=[
            band_param,
        ],
    )
    @action(detail=True, url_path=r'band/(?P<band>\w+)')
    def band(self, request: Request, pk: int, band: int) -> Response:
        tile_source = self._get_tile_source(request, pk)
        metadata = tile_source.getOneBandInformation(int(band))
        return Response(metadata)
