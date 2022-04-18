import base64
import binascii
import json
from typing import Union

from large_image.exceptions import TileSourceError
from large_image.tilesource import FileTileSource
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.request import Request

from django_large_image import tilesource, utilities

CACHE_TIMEOUT = 60 * 60 * 2


class LargeImageMixinBase:
    def get_path(self, request: Request, pk: int = None) -> str:
        """Return path on disk to image file (or VSI str).

        This can be overridden downstream to implement custom FUSE, etc.,
        interfaces.

        Returns
        -------
        str : The local file path to pass to large_image

        """
        raise NotImplementedError('You must implement `get_path` on your viewset.')

    def get_style(self, request: Request) -> dict:
        # Check for base64 encoded style dict
        if 'style' in request.query_params:
            style = request.query_params.get('style')
            # Un Base64 the string
            if utilities.is_base64(style):
                try:
                    message_bytes = base64.b64decode(style.encode('ascii'))
                    style = json.loads(message_bytes.decode('ascii'))
                except (json.JSONDecodeError, binascii.Error) as e:
                    raise ValidationError(
                        f'`style` query parameter is malformed and likely not base64 encoded: {e}'
                    )
            else:
                try:
                    style = json.loads(style)
                except json.JSONDecodeError as e:
                    raise ValidationError(
                        f'`style` query parameter is malformed and likely not properly URL encoded: {e}'
                    )
        # else, fallback to supported query parameters for viewing a sinlge band
        else:
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
                palette = request.query_params.get(
                    'palette', request.query_params.get('cmap', None)
                )
                if not utilities.param_nully(palette):
                    style['palette'] = palette
                nodata = request.query_params.get('nodata', None)
                if not utilities.param_nully(nodata):
                    style['nodata'] = nodata
                scheme = request.query_params.get('scheme', None)
                if not utilities.param_nully:
                    style['scheme'] = scheme
        return style

    def open_tile_source(self, path, *args, **kwargs) -> FileTileSource:
        """Override to open with a specific large-image source."""
        return tilesource.get_tilesource_from_path(path, *args, **kwargs)

    def open_image(
        self,
        request: Request,
        path: str,
        encoding: str = None,
        style: Union[bool, dict, str] = True,
    ) -> FileTileSource:
        projection = request.query_params.get('projection', None)
        kwargs = {}
        if encoding:
            kwargs['encoding'] = encoding
        if encoding:
            kwargs['encoding'] = encoding
        if style:
            if isinstance(style, bool) and style:
                _style = json.dumps(self.get_style(request))
            elif isinstance(style, dict) and style:
                _style = json.dumps(style)
            if isinstance(_style, str) and not utilities.param_nully(_style):
                kwargs['style'] = _style
        if projection:
            kwargs['projection'] = projection
        return self.open_tile_source(path, **kwargs)

    def get_tile_source(
        self,
        request: Request,
        pk: int = None,
        encoding: str = None,
        style: Union[bool, dict] = True,
    ) -> FileTileSource:
        """Return the built tile source."""
        try:
            return self.open_image(
                request, self.get_path(request, pk), encoding=encoding, style=style
            )
        except TileSourceError as e:
            # Raise 500 server error if tile source failed to open
            raise APIException(str(e))
