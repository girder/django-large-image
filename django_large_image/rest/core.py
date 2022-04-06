import json
import logging

from large_image.tilesource import FileTileSource
from rest_framework.exceptions import APIException
from rest_framework.request import Request
from rest_framework.views import APIView

from django_large_image import tilesource, utilities

logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 60 * 60 * 2


class BaseLargeImageView(APIView):
    FILE_FIELD_NAME: str = None

    def get_field_file(self):
        """Get `FileField` using `FILE_FIELD_NAME`."""
        try:
            return getattr(self.get_object(), self.FILE_FIELD_NAME)
        except (AttributeError, TypeError):
            # Raise 500 server error
            raise APIException('`FILE_FIELD_NAME` not properly set on viewset class.')

    def get_path(self, request: Request, pk: int):
        """Return path on disk to image file (or VSI str).

        This can be overridden downstream to implement custom FUSE, etc.,
        interfaces.

        Returns
        -------
        str : The local file path to pass to large_image

        """
        return utilities.field_file_to_local_path(self.get_field_file())

    def _get_style(self, request: Request):
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

    def _open_image(self, request: Request, path: str):
        projection = request.query_params.get('projection', None)
        style = self._get_style(request)
        return tilesource.get_tilesource_from_path(path, projection, style=style)

    def _get_tile_source(self, request: Request, pk: int) -> FileTileSource:
        """Return the built tile source."""
        return self._open_image(request, self.get_path(request, pk))
