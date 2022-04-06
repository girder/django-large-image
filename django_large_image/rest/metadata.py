from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from django_large_image import tilesource
from django_large_image.rest import params
from django_large_image.rest.base import BaseLargeImageView


class MetaData(BaseLargeImageView):
    @swagger_auto_schema(
        method='GET',
        operation_summary='Returns tile metadata.',
        manual_parameters=[params.projection],
    )
    @action(detail=True)
    def metadata(self, request: Request, pk: int) -> Response:
        source = self.get_tile_source(request, pk)
        metadata = tilesource.get_metadata(source)
        return Response(metadata)

    """Returns additional known metadata about the tile source."""

    @swagger_auto_schema(
        method='GET',
        operation_summary='Returns additional known metadata about the tile source.',
        manual_parameters=[params.projection],
    )
    @action(detail=True)
    def internal_metadata(self, request: Request, pk: int) -> Response:
        source = self.get_tile_source(request, pk)
        metadata = tilesource.get_internal_metadata(source)
        return Response(metadata)

    @swagger_auto_schema(
        method='GET',
        operation_summary='Returns bands information.',
        manual_parameters=[params.projection],
    )
    @action(detail=True)
    def bands(self, request: Request, pk: int) -> Response:
        source = self.get_tile_source(request, pk)
        metadata = source.getBandInformation()
        return Response(metadata)

    @swagger_auto_schema(
        method='GET',
        operation_summary='Returns single band information.',
        manual_parameters=[
            params.projection,
            params.band,
        ],
    )
    @action(detail=True)
    def band(self, request: Request, pk: int) -> Response:
        band = int(request.query_params.get('band', 1))
        source = self.get_tile_source(request, pk)
        metadata = source.getOneBandInformation(band)
        return Response(metadata)
