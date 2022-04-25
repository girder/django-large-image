import json
import pathlib
from typing import Any, Optional, Union

from large_image.exceptions import TileSourceError
from large_image.tilesource import FileTileSource
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.request import Request

from django_large_image import tilesource, utilities

CACHE_TIMEOUT = 60 * 60 * 2


class LargeImageMixinBase:
    def get_path(self, request: Request, pk: int = None) -> Union[str, pathlib.Path]:
        """Return path on disk to image file (or VSI str).

        This can be overridden downstream to implement custom FUSE, etc.,
        interfaces.

        Returns
        -------
        str : The local file path to pass to large_image

        """
        raise NotImplementedError(
            'You must implement `get_path` on your viewset.'
        )  # pragma: no cover

    def get_query_param(self, request: Request, key: str, default: Optional[Any] = '') -> str:
        return request.query_params.get(key, str(default))

    def get_style(self, request: Request) -> dict:
        # Check for url encoded style JSON
        if 'style' in request.query_params:
            try:
                style = json.loads(self.get_query_param(request, 'style'))
            except json.JSONDecodeError as e:
                raise ValidationError(
                    f'`style` query parameter is malformed and likely not properly URL encoded: {e}'
                )
        # else, fallback to supported query parameters for viewing a sinlge band
        else:
            band = int(self.get_query_param(request, 'band', 0))
            style = None
            if band:  # bands are 1-indexed
                style = {'band': band}
                bmin = self.get_query_param(request, 'min')
                bmax = self.get_query_param(request, 'max')
                if not utilities.param_nully(bmin):
                    style['min'] = bmin
                if not utilities.param_nully(bmax):
                    style['max'] = bmax
                palette = self.get_query_param(
                    request, 'palette', self.get_query_param(request, 'cmap')
                )
                if not utilities.param_nully(palette):
                    style['palette'] = palette
                nodata = self.get_query_param(request, 'nodata')
                if not utilities.param_nully(nodata):
                    style['nodata'] = nodata
                scheme = self.get_query_param(request, 'scheme')
                if not utilities.param_nully(scheme):
                    style['scheme'] = scheme
        return style

    def open_tile_source(
        self, request: Request, path: Union[str, pathlib.Path], **kwargs
    ) -> FileTileSource:
        """Override to open with a specific large-image source."""
        source = self.get_query_param(request, 'source')
        # error: "get_tilesource_from_path" gets multiple values for keyword
        # argument "source" Found 1 error in 1 file (checked 15 source files)
        return tilesource.get_tilesource_from_path(path, source=source, **kwargs)  # type: ignore

    def open_image(
        self,
        request: Request,
        path: Union[str, pathlib.Path],
        encoding: str = None,
        style: Union[bool, dict, str] = True,
    ) -> FileTileSource:
        projection = self.get_query_param(request, 'projection')
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
        return self.open_tile_source(request, path, **kwargs)

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
