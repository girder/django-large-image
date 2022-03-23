import json
import logging

# from django.core.cache import cache
from large_image.exceptions import TileSourceFileNotFoundError
from large_image.tilesource import FileTileSource
from rest_framework.request import Request
from rest_framework.views import APIView

from django_large_image import utilities

logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 60 * 60 * 2


class BaseLargeImageView(APIView):
    FILE_FIELD_NAME: str = None
    USE_VSI: bool = False

    def get_path(self, pk: int, use_vsi: bool = False):
        """Return path on disk to image file (or VSI str).

        This can be overridden downstream to implement custom FUSE, etc.,
        interfaces.

        Parameters
        ----------
        pk : int
            Model instance primary key

        use_vsi : bool, optional
            A boolean to use GDALs VFS/VSI.

        Returns
        -------
        str : The file path or vsi string to pass to large_image

        """
        # Get FileField using FILE_FIELD_NAME
        field_file = getattr(self.get_object(), self.FILE_FIELD_NAME)
        if use_vsi:
            with utilities.patch_internal_presign(field_file):
                # Grab URL and pass back VSI path
                return utilities.make_vsi(field_file.url)
        # Checkout file locally
        return utilities.field_file_to_local_path(field_file)

    def _get_style(self, request: Request):
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
        return style

    def _open_image(self, request: Request, path: str, default_projection: str = 'EPSG:3857'):
        projection = request.query_params.get('projection', default_projection)
        style = self._get_style(request)
        return utilities.get_tilesource_from_image(path, projection, style=style)

    def _get_tile_source(
        self, request: Request, pk: int, default_projection: str = 'EPSG:3857'
    ) -> FileTileSource:
        """Return the built tile source."""
        # get image_entry from cache
        # image_cache_key = f'large_image_tile:image_{pk}'
        # if (image_entry := cache.get(image_cache_key, None)) is None:
        #     image_entry = get_object_or_404(Image, pk=pk)
        #     cache.set(image_cache_key, image_entry, CACHE_TIMEOUT)
        if self.USE_VSI:
            try:
                return self._open_image(
                    request, self.get_path(pk, use_vsi=True), default_projection=default_projection
                )
            except TileSourceFileNotFoundError:
                pass
        return self._open_image(request, self.get_path(pk), default_projection=default_projection)
