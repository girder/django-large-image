import json
import logging
from pathlib import PurePath

# from django.core.cache import cache
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import large_image
from large_image.tilesource import FileTileSource
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from django_large_image import utilities

logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 60 * 60 * 2

z_param = openapi.Parameter(
    'z', openapi.IN_PATH, description='zoom level', type=openapi.TYPE_INTEGER
)
x_param = openapi.Parameter('x', openapi.IN_PATH, description='x', type=openapi.TYPE_INTEGER)
y_param = openapi.Parameter('y', openapi.IN_PATH, description='y', type=openapi.TYPE_INTEGER)
band_param = openapi.Parameter(
    'band', openapi.IN_PATH, description='band index', type=openapi.TYPE_INTEGER
)
left_param = openapi.Parameter(
    'left', openapi.IN_PATH, description='left', type=openapi.TYPE_NUMBER
)
right_param = openapi.Parameter(
    'right', openapi.IN_PATH, description='right', type=openapi.TYPE_NUMBER
)
top_param = openapi.Parameter('top', openapi.IN_PATH, description='top', type=openapi.TYPE_NUMBER)
bottom_param = openapi.Parameter(
    'bottom', openapi.IN_PATH, description='bottom', type=openapi.TYPE_NUMBER
)


class ListTileSourcesView(APIView):
    def get(self, request: Request) -> Response:
        large_image.tilesource.loadTileSources()
        sources = large_image.tilesource.AvailableTileSources
        return Response({k: str(v) for k, v in sources.items()})


class ListColormapsView(APIView):
    def get(self, request: Request) -> Response:
        """List of available palettes.

        This does not currently list the palettable palettes there isn't a clean
        way to list all of them.
        """
        simple = {
            'red': ['#000', '#f00'],
            'r': ['#000', '#f00'],
            'green': ['#000', '#0f0'],
            'g': ['#000', '#0f0'],
            'blue': ['#000', '#00f'],
            'b': ['#000', '#00f'],
        }
        cmaps = {}
        try:
            import matplotlib.pyplot

            cmaps['matplotlib'] = list(matplotlib.pyplot.colormaps())
        except ImportError:
            logger.error('Install matplotlib for additional colormap choices.')
        cmaps['simple'] = [s for s in simple.keys() if len(s) > 1]
        return Response(cmaps)


class LargeImageView(APIView):
    FILE_FIELD_NAME = None

    def _get_path(self, pk: int):
        # Get FileField using FILE_FIELD_NAME
        field_file = getattr(self.get_object(), self.FILE_FIELD_NAME)
        # Get local file path
        field_file_basename = PurePath(field_file.name).name
        directory = utilities.get_cache_dir() / f'f-{pk}'
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / field_file_basename
        # Checkout file locally - or configure VSI
        return utilities.field_file_to_local_path(field_file, path)

    def _get_tile_source(
        self, request: Request, pk: int, default_projection: str = 'EPSG:3857'
    ) -> FileTileSource:
        """Return the built tile source."""
        # get image_entry from cache
        # image_cache_key = f'large_image_tile:image_{pk}'
        # if (image_entry := cache.get(image_cache_key, None)) is None:
        #     image_entry = get_object_or_404(Image, pk=pk)
        #     cache.set(image_cache_key, image_entry, CACHE_TIMEOUT)
        path = self._get_path(pk)

        projection = request.query_params.get('projection', default_projection)
        band = int(request.query_params.get('band', 0))
        style = None
        if band:
            style = {'band': band}
            bmin = request.query_params.get('min', None)
            bmax = request.query_params.get('max', None)
            if bmin is not None:
                style['min'] = bmin
            if bmax is not None:
                style['max'] = bmax
            palette = request.query_params.get('palette', None)
            if palette:
                style['palette'] = palette
            nodata = request.query_params.get('nodata', None)
            if nodata:
                style['nodata'] = nodata
            style = json.dumps(style)
        return utilities.get_tilesource_from_image(path, projection, style=style)

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
        operation_summary='Returns tile image.',
        manual_parameters=[z_param, x_param, y_param],
    )
    @action(detail=True, url_path=r'tiles/(?P<z>\w+)/(?P<x>\w+)/(?P<y>\w+).png')
    def tile(self, request: Request, pk: int, x: int, y: int, z: int) -> HttpResponse:
        tile_source = self._get_tile_source(request, pk)
        tile_binary = tile_source.getTile(int(x), int(y), int(z))
        mime_type = tile_source.getTileMimeType()
        return HttpResponse(tile_binary, content_type=mime_type)

    @swagger_auto_schema(
        method='GET',
        operation_summary='Returns bounds of a tile for a given x, y, z index.',
        manual_parameters=[z_param, x_param, y_param],
    )
    @action(
        detail=True, methods=['get'], url_path=r'tiles/(?P<z>\w+)/(?P<x>\w+)/(?P<y>\w+)/corners'
    )
    def tile_corners(self, request: Request, pk: int, x: int, y: int, z: int) -> HttpResponse:
        tile_source = self._get_tile_source(request, pk)
        xmin, ymin, xmax, ymax = tile_source.getTileCorners(int(z), int(x), int(y))
        metadata = {
            'xmin': xmin,
            'xmax': xmax,
            'ymin': ymin,
            'ymax': ymax,
            'proj4': tile_source.getProj4String(),
        }
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
