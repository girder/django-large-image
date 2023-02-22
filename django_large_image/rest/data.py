from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from django_large_image import tilesource, utilities
from django_large_image.rest import params
from django_large_image.rest.base import LargeImageMixinBase
from django_large_image.rest.renderers import image_data_renderers, image_renderers

thumbnail_summary = 'Returns thumbnail of full image.'
thumbnail_parameters = params.BASE + params.THUMBNAIL + params.STYLE
region_summary = 'Returns region tile binary.'
region_parameters = params.BASE + params.REGION
pixel_summary = 'Returns single pixel.'
pixel_parameters = params.BASE + [params.left, params.top] + params.STYLE
histogram_summary = 'Returns histogram'
histogram_parameters = params.BASE + params.HISTOGRAM


class DataMixin(LargeImageMixinBase):
    @extend_schema(
        methods=['GET'],
        summary=thumbnail_summary,
        parameters=thumbnail_parameters,
    )
    @action(
        detail=False,
        url_path=f'data/thumbnail.{params.FORMAT_URL_PATTERN}',
        renderer_classes=image_renderers,
    )
    def thumbnail(
        self, request: Request, pk: int = None, fmt: str = 'png', **kwargs
    ) -> HttpResponse:
        encoding = tilesource.format_to_encoding(fmt)
        width = int(self.get_query_param(request, 'max_width', 256))
        height = int(self.get_query_param(request, 'max_height', 256))
        source = self.get_tile_source(request, pk, encoding=encoding)
        thumb_data, mime_type = source.getThumbnail(encoding=encoding, width=width, height=height)
        return HttpResponse(thumb_data, content_type=mime_type)

    @extend_schema(
        methods=['GET'],
        summary=region_summary,
        parameters=region_parameters + params.STYLE,
    )
    @action(
        detail=False,
        url_path=f'data/region.{params.FORMAT_URL_PATTERN}',
        renderer_classes=image_data_renderers,
    )
    def region(self, request: Request, pk: int = None, fmt: str = 'tiff', **kwargs) -> HttpResponse:
        """Return the region tile binary from world coordinates in given EPSG.

        Note
        ----
        Use the `units` query parameter to inidicate the projection of the given
        coordinates. This can be different than the `projection` parameter used
        to open the tile source. `units` defaults to `EPSG:4326` for geospatial
        images, otherwise, must use `pixels`.

        """
        source = self.get_tile_source(request, pk)
        units = self.get_query_param(request, 'units')
        encoding = tilesource.format_to_encoding(fmt)
        left = float(self.get_query_param(request, 'left'))
        right = float(self.get_query_param(request, 'right'))
        top = float(self.get_query_param(request, 'top'))
        bottom = float(self.get_query_param(request, 'bottom'))
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

    @extend_schema(
        methods=['GET'],
        summary=pixel_summary,
        parameters=pixel_parameters,
    )
    @action(detail=False, url_path='data/pixel')
    def pixel(self, request: Request, pk: int = None, **kwargs) -> Response:
        left = int(self.get_query_param(request, 'left'))
        top = int(self.get_query_param(request, 'top'))
        source = self.get_tile_source(request, pk)
        metadata = source.getPixel(region={'left': left, 'top': top, 'units': 'pixels'})
        return Response(metadata)

    @extend_schema(
        methods=['GET'],
        summary=histogram_summary,
        parameters=histogram_parameters,
    )
    @action(detail=False, url_path='data/histogram')
    def histogram(self, request: Request, pk: int = None, **kwargs) -> Response:
        only_min_max = not utilities.param_nully(self.get_query_param(request, 'onlyMinMax', False))
        density = not utilities.param_nully(self.get_query_param(request, 'density', False))
        kwargs = dict(
            onlyMinMax=only_min_max,
            bins=int(self.get_query_param(request, 'bins', 256)),
            density=density,
            format=self.get_query_param(request, 'format'),
        )
        source = self.get_tile_source(request, pk, style=False)
        result = source.histogram(**kwargs)
        if 'histogram' in result:
            result = result['histogram']
            for entry in result:
                for key in {'bin_edges', 'hist', 'range'}:
                    if key in entry:
                        entry[key] = [float(val) for val in list(entry[key])]
                for key in {'min', 'max', 'samples'}:
                    if key in entry:
                        entry[key] = float(entry[key])
        return Response(result)


class DataDetailMixin(DataMixin):
    @extend_schema(
        methods=['GET'],
        summary=thumbnail_summary,
        parameters=thumbnail_parameters,
    )
    @action(
        detail=True,
        url_path=f'data/thumbnail.{params.FORMAT_URL_PATTERN}',
        renderer_classes=image_renderers,
    )
    def thumbnail(
        self, request: Request, pk: int = None, fmt: str = 'png', **kwargs
    ) -> HttpResponse:
        return super().thumbnail(request, pk, fmt)

    @extend_schema(
        methods=['GET'],
        summary=region_summary,
        parameters=region_parameters + params.STYLE,
    )
    @action(
        detail=True,
        url_path=f'data/region.{params.FORMAT_URL_PATTERN}',
        renderer_classes=image_data_renderers,
    )
    def region(self, request: Request, pk: int = None, fmt: str = 'tiff', **kwargs) -> HttpResponse:
        return super().region(request, pk, fmt)

    @extend_schema(
        methods=['GET'],
        summary=pixel_summary,
        parameters=pixel_parameters,
    )
    @action(detail=True, url_path='data/pixel')
    def pixel(self, request: Request, pk: int = None, **kwargs) -> Response:
        return super().pixel(request, pk)

    @extend_schema(
        methods=['GET'],
        summary=histogram_summary,
        parameters=histogram_parameters,
    )
    @action(detail=True, url_path='data/histogram')
    def histogram(self, request: Request, pk: int = None, **kwargs) -> Response:
        return super().histogram(request, pk)
