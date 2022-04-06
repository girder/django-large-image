import json
import logging

from large_image.tilesource import FileTileSource
from rest_framework.request import Request

from django_large_image import tilesource, utilities

logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 60 * 60 * 2


class LargeImageViewMixinBase:
    def get_path(self, request: Request, pk: int):
        """Return path on disk to image file (or VSI str).

        This can be overridden downstream to implement custom FUSE, etc.,
        interfaces.

        Returns
        -------
        str : The local file path to pass to large_image

        """
        raise NotImplementedError

    def get_style(self, request: Request):
        band = int(request.query_params.get('band', 0))
        style = None
        if band:  # bands are 1-indexed
            style = {'band': band}
            bmin = request.query_params.get('min', None)
            bmax = request.query_params.get('max', None)
            if not utilities.param_nully(bmin):
                style['min'] = bmin
            if not utilities.param_nully(bmax):
                style['max'] = bmax
            palette = request.query_params.get('palette', None)
            if not utilities.param_nully(palette):
                style['palette'] = palette
            nodata = request.query_params.get('nodata', None)
            if not utilities.param_nully(nodata):
                style['nodata'] = nodata
            style = json.dumps(style)
        return style

    def open_image(self, request: Request, path: str):
        projection = request.query_params.get('projection', None)
        style = self.get_style(request)
        return tilesource.get_tilesource_from_path(path, projection, style=style)

    def get_tile_source(self, request: Request, pk: int) -> FileTileSource:
        """Return the built tile source."""
        return self.open_image(request, self.get_path(request, pk))
