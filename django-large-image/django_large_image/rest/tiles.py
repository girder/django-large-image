import json

from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_large_image import utilities
from django_large_image.models import Image
import large_image
from large_image.tilesource import FileTileSource
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

CACHE_TIMEOUT = 60 * 60 * 2


class ListTileSourcesView(APIView):
    def get(self, request: Request) -> Response:
        large_image.tilesource.loadTileSources()
        sources = large_image.tilesource.AvailableTileSources
        return Response({k: str(v) for k, v in sources.items()})


class BaseTileView(APIView):
    def get_tile_source(
        self, request: Request, pk: int, default_projection: str = 'EPSG:3857'
    ) -> FileTileSource:
        """Return the built tile source."""
        # get image_entry from cache
        image_cache_key = f'large_image_tile:image_{pk}'
        if (image_entry := cache.get(image_cache_key, None)) is None:
            image_entry = get_object_or_404(Image, pk=pk)
            cache.set(image_cache_key, image_entry, CACHE_TIMEOUT)

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
        return utilities.get_tilesource_from_image(image_entry, projection, style=style)


class TileMetadataView(BaseTileView):
    """Returns tile metadata."""

    def get(self, request: Request, pk: int) -> Response:
        tile_source = self.get_tile_source(request, pk)
        metadata = tile_source.getMetadata()
        metadata.setdefault('geospatial', False)
        if metadata['geospatial']:
            bounds = utilities.get_tile_bounds(tile_source)
            metadata['bounds'] = bounds
        return Response(metadata)


class TileInternalMetadataView(BaseTileView):
    """Returns additional known metadata about the tile source."""

    def get(self, request: Request, pk: int) -> Response:
        tile_source = self.get_tile_source(request, pk)
        metadata = tile_source.getInternalMetadata()
        metadata.setdefault('geospatial', False)
        if metadata['geospatial']:
            bounds = utilities.get_tile_bounds(tile_source)
            metadata['bounds'] = bounds
        return Response(metadata)


class TileView(BaseTileView):
    """Returns tile binary."""

    @method_decorator(cache_page(CACHE_TIMEOUT))
    def get(self, request: Request, pk: int, x: int, y: int, z: int) -> HttpResponse:
        tile_source = self.get_tile_source(request, pk)
        tile_binary = tile_source.getTile(x, y, z)
        mime_type = tile_source.getTileMimeType()
        return HttpResponse(tile_binary, content_type=mime_type)


class TileCornersView(BaseTileView):
    """Returns bounds of a tile for a given x, y, z index."""

    def get(self, request: Request, pk: int, x: int, y: int, z: int) -> HttpResponse:
        tile_source = self.get_tile_source(request, pk)
        xmin, ymin, xmax, ymax = tile_source.getTileCorners(z, x, y)
        metadata = {
            'xmin': xmin,
            'xmax': xmax,
            'ymin': ymin,
            'ymax': ymax,
            'proj4': tile_source.getProj4String(),
        }
        return Response(metadata)


class TileThumnailView(BaseTileView):
    """Returns tile thumbnail."""

    @method_decorator(cache_page(CACHE_TIMEOUT))
    def get(self, request: Request, pk: int) -> HttpResponse:
        tile_source = self.get_tile_source(request, pk)
        thumb_data, mime_type = tile_source.getThumbnail(encoding='PNG')
        return HttpResponse(thumb_data, content_type=mime_type)


class TileBandInfoView(BaseTileView):
    """Returns band information."""

    def get(self, request: Request, pk: int) -> Response:
        tile_source = self.get_tile_source(request, pk)
        metadata = tile_source.getBandInformation()
        return Response(metadata)


class TileSingleBandInfoView(BaseTileView):
    """Returns single band information."""

    def get(self, request: Request, pk: int, band: int) -> Response:
        tile_source = self.get_tile_source(request, pk)
        metadata = tile_source.getOneBandInformation(band)
        return Response(metadata)


class TileRegionView(BaseTileView):
    """Returns region tile binary from world coordinates in given EPSG.

    Note
    ----
    Use the `units` query parameter to inidicate the projection of the given
    coordinates. This can be different than the `projection` parameter used
    to open the tile source. `units` defaults to `EPSG:4326` for geospatial
    images, otherwise, must use `pixels`.

    """

    def get(
        self, request: Request, pk: int, left: float, right: float, bottom: float, top: float
    ) -> HttpResponse:
        tile_source = self.get_tile_source(request, pk)
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


class TilePixelView(BaseTileView):
    """Returns single pixel."""

    def get(self, request: Request, pk: int, left: int, top: int) -> Response:
        tile_source = self.get_tile_source(request, pk, default_projection=None)
        metadata = tile_source.getPixel(region={'left': left, 'top': top, 'units': 'pixels'})
        return Response(metadata)


class TileHistogramView(BaseTileView):
    """Returns histogram."""

    def get(self, request: Request, pk: int) -> Response:
        kwargs = dict(
            onlyMinMax=request.query_params.get('onlyMinMax', False),
            bins=int(request.query_params.get('bins', 256)),
            density=request.query_params.get('density', False),
            format=request.query_params.get('format', None),
        )
        tile_source = self.get_tile_source(request, pk, default_projection=None)
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
