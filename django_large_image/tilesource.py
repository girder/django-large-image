"""large-image utilities."""
from contextlib import contextmanager
import os
import pathlib
import tempfile

import large_image
from large_image.tilesource import FileTileSource

from django_large_image import utilities


def get_tilesource_from_path(
    path: str, projection: str = None, style: str = None, encoding: str = 'PNG'
) -> FileTileSource:
    return large_image.open(str(path), projection=projection, style=style, encoding=encoding)


@contextmanager
def yeild_tilesource_from_path(path: str, projection: str = None) -> FileTileSource:
    yield get_tilesource_from_path(path, projection)


def is_geospatial(source: FileTileSource):
    return source.getMetadata().get('geospatial', False)


def _get_region(source: FileTileSource, region: dict, encoding: str):
    result, mime_type = source.getRegion(region=region, encoding=encoding)
    if encoding == 'TILED':
        path = result
    else:
        # Write content to temporary file
        fd, path = tempfile.mkstemp(
            suffix=f'.{encoding}', prefix='pixelRegion_', dir=str(utilities.get_cache_dir())
        )
        os.close(fd)
        path = pathlib.Path(path)
        with open(path, 'wb') as f:
            f.write(result)
    return path, mime_type


def get_region(
    source: FileTileSource,
    left: float,
    right: float,
    bottom: float,
    top: float,
    units: str = None,
    encoding: str = None,
):
    geospatial = hasattr(source, 'geospatial') and source.geospatial
    if encoding is None and geospatial:
        # Use tiled encoding by default for geospatial rasters
        #   output will be a tiled TIF
        encoding = 'TILED'
    elif encoding is None:
        # Use JPEG encoding by default for nongeospatial rasters
        encoding = 'JPEG'
    if geospatial and units not in [
        'pixels',
    ]:
        if units is None:
            units = 'EPSG:4326'
        region = dict(left=left, right=right, bottom=bottom, top=top, units=units)
        return _get_region(source, region, encoding)
    units = 'pixels'
    left, right = min(left, right), max(left, right)
    top, bottom = min(top, bottom), max(top, bottom)
    region = dict(left=left, right=right, bottom=bottom, top=top, units=units)
    return _get_region(source, region, encoding)


def get_tile_bounds(
    source: FileTileSource,
    projection: str = 'EPSG:4326',
):
    bounds = source.getBounds(srs=projection)
    if not bounds:
        return
    threshold = 89.9999
    for key in ('ymin', 'ymax'):
        bounds[key] = max(min(bounds[key], threshold), -threshold)
    return bounds
