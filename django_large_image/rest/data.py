from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from django_large_image import tilesource
from django_large_image.rest import params
from django_large_image.rest.base import CACHE_TIMEOUT, LargeImageViewSetMixinBase


class DataMixin(LargeImageViewSetMixinBase):
    def thumbnail(self, request: Request, pk: int, format: str = None) -> HttpResponse:
        encoding = tilesource.format_to_encoding(format)
        source = self.get_tile_source(request, pk, encoding=encoding)
        thumb_data, mime_type = source.getThumbnail(encoding=encoding)
        return HttpResponse(thumb_data, content_type=mime_type)

    @method_decorator(cache_page(CACHE_TIMEOUT))
    @swagger_auto_schema(
        method='GET',
        operation_summary='Returns thumbnail of full image as PNG.',
        manual_parameters=[params.projection] + params.STYLE,
    )
    @action(detail=True, url_path='thumbnail.png')
    def thumbnail_png(self, request: Request, pk: int) -> HttpResponse:
        return self.thumbnail(request, pk, format='png')

    @method_decorator(cache_page(CACHE_TIMEOUT))
    @swagger_auto_schema(
        method='GET',
        operation_summary='Returns thumbnail of full image as JPEG.',
        manual_parameters=[params.projection] + params.STYLE,
    )
    @action(detail=True, url_path='thumbnail.jpeg')
    def thumbnail_jpeg(self, request: Request, pk: int) -> HttpResponse:
        return self.thumbnail(request, pk, format='jpeg')

    def region(self, request: Request, pk: int, format: str = None) -> HttpResponse:
        """Return the region tile binary from world coordinates in given EPSG.

        Note
        ----
        Use the `units` query parameter to inidicate the projection of the given
        coordinates. This can be different than the `projection` parameter used
        to open the tile source. `units` defaults to `EPSG:4326` for geospatial
        images, otherwise, must use `pixels`.

        """
        source = self.get_tile_source(request, pk)
        units = request.query_params.get('units', None)
        encoding = tilesource.format_to_encoding(format)
        left = float(request.query_params.get('left'))
        right = float(request.query_params.get('right'))
        top = float(request.query_params.get('top'))
        bottom = float(request.query_params.get('bottom'))
        path, mime_type = tilesource.get_region(
            source,
            left,
            right,
            bottom,
            top,
            units,
            encoding,
        )
        if not path:
            raise ValidationError(
                'No output generated, check that the bounds of your ROI overlap source imagery and that your `projection` and `units` are correct.'
            )
        tile_binary = open(path, 'rb')
        return HttpResponse(tile_binary, content_type=mime_type)

    @swagger_auto_schema(
        method='GET',
        operation_summary='Returns region tile binary from world coordinates in given EPSG as a tiled tif image.',
        manual_parameters=[params.projection] + params.REGION,
    )
    @action(
        detail=True,
        url_path=r'region.tif',
    )
    def region_tif(self, request: Request, pk: int) -> HttpResponse:
        return self.region(request, pk, format='tif')

    @swagger_auto_schema(
        method='GET',
        operation_summary='Returns region tile binary from world coordinates in given EPSG as a png image.',
        manual_parameters=[params.projection] + params.REGION,
    )
    @action(
        detail=True,
        url_path=r'region.png',
    )
    def region_png(self, request: Request, pk: int) -> HttpResponse:
        return self.region(request, pk, format='png')

    @swagger_auto_schema(
        method='GET',
        operation_summary='Returns region tile binary from world coordinates in given EPSG as a jpeg image.',
        manual_parameters=[params.projection] + params.REGION,
    )
    @action(
        detail=True,
        url_path=r'region.jpeg',
    )
    def region_jpeg(self, request: Request, pk: int) -> HttpResponse:
        return self.region(request, pk, format='jpeg')

    @swagger_auto_schema(
        method='GET',
        operation_summary='Returns single pixel.',
        manual_parameters=[params.projection, params.left, params.top] + params.STYLE,
    )
    @action(detail=True)
    def pixel(self, request: Request, pk: int) -> Response:
        left = float(request.query_params.get('left'))
        top = float(request.query_params.get('top'))
        source = self.get_tile_source(request, pk)
        metadata = source.getPixel(region={'left': int(left), 'top': int(top), 'units': 'pixels'})
        return Response(metadata)

    @swagger_auto_schema(
        method='GET',
        operation_summary='Returns histogram',
        manual_parameters=[params.projection] + params.HISTOGRAM,
    )
    @action(detail=True)
    def histogram(self, request: Request, pk: int) -> Response:
        kwargs = dict(
            # TODO: add openapi params for these
            onlyMinMax=request.query_params.get('onlyMinMax', False),
            bins=int(request.query_params.get('bins', 256)),
            density=request.query_params.get('density', False),
            format=request.query_params.get('format', None),
        )
        source = self.get_tile_source(request, pk)
        result = source.histogram(**kwargs)
        result = result['histogram']
        for entry in result:
            for key in {'bin_edges', 'hist', 'range'}:
                if key in entry:
                    entry[key] = [float(val) for val in list(entry[key])]
            for key in {'min', 'max', 'samples'}:
                if key in entry:
                    entry[key] = float(entry[key])
        return Response(result)
