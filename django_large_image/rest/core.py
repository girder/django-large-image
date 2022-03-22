import json
import logging
from pathlib import PurePath

# from django.core.cache import cache
from large_image.tilesource import FileTileSource
from rest_framework.request import Request
from rest_framework.views import APIView

from django_large_image import utilities

logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 60 * 60 * 2


class BaseLargeImageView(APIView):
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
