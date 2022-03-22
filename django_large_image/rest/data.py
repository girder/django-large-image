from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from django_large_image import utilities
from django_large_image.rest.core import BaseLargeImageView
from django_large_image.rest.params import bottom_param, left_param, right_param, top_param


class Data(BaseLargeImageView):
    @swagger_auto_schema(
        method='GET',
        operation_summary='Returns region tile binary from world coordinates in given EPSG.',
        manual_parameters=[left_param, right_param, bottom_param, top_param],
    )
    @action(
        detail=True,
        url_path=r'region/(?P<left>\w+)/(?P<right>\w+)/(?P<bottom>\w+)/(?P<top>\w+)/region.tif',
    )
    def region(
        self, request: Request, pk: int, left: float, right: float, bottom: float, top: float
    ) -> HttpResponse:
        """Return the region tile binary from world coordinates in given EPSG.

        Note
        ----
        Use the `units` query parameter to inidicate the projection of the given
        coordinates. This can be different than the `projection` parameter used
        to open the tile source. `units` defaults to `EPSG:4326` for geospatial
        images, otherwise, must use `pixels`.

        """
        tile_source = self._get_tile_source(request, pk)
        units = request.query_params.get('units', None)
        encoding = request.query_params.get('encoding', None)
        path, mime_type = utilities.get_region(
            tile_source,
            left,
            right,
            bottom,
            top,
            units,
            encoding,
        )
        if not path:
            # TODO: should this raise error status?
            return HttpResponse(b'', content_type=mime_type)
        tile_binary = open(path, 'rb')
        return HttpResponse(tile_binary, content_type=mime_type)

    @swagger_auto_schema(
        method='GET',
        operation_summary='Returns single pixel.',
        manual_parameters=[left_param, top_param],
    )
    @action(detail=True, url_path=r'pixel/(?P<left>\w+)/(?P<top>\w+)')
    def pixel(self, request: Request, pk: int, left: int, top: int) -> Response:
        tile_source = self._get_tile_source(request, pk, default_projection=None)
        metadata = tile_source.getPixel(
            region={'left': int(left), 'top': int(top), 'units': 'pixels'}
        )
        return Response(metadata)

    @swagger_auto_schema(
        method='GET',
        operation_summary='Returns histogram',
    )
    @action(detail=True)
    def histogram(self, request: Request, pk: int) -> Response:
        kwargs = dict(
            onlyMinMax=request.query_params.get('onlyMinMax', False),
            bins=int(request.query_params.get('bins', 256)),
            density=request.query_params.get('density', False),
            format=request.query_params.get('format', None),
        )
        tile_source = self._get_tile_source(request, pk, default_projection=None)
        result = tile_source.histogram(**kwargs)
        result = result['histogram']
        for entry in result:
            for key in {'bin_edges', 'hist', 'range'}:
                if key in entry:
                    entry[key] = [float(val) for val in list(entry[key])]
            for key in {'min', 'max', 'samples'}:
                if key in entry:
                    entry[key] = float(entry[key])
        return Response(result)
