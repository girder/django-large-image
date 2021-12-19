from contextlib import contextmanager
import os
import pathlib
import tempfile
from typing import Any

from django.conf import settings
from django_large_image.models import Image
import large_image
from large_image.tilesource import FileTileSource


def get_or_create_no_commit(model: Any, defaults: dict = None, **kwargs):
    try:
        return model.objects.get(**kwargs), False
    except model.DoesNotExist:
        if not defaults:
            defaults = {}
        defaults.update(kwargs)
        return model(**defaults), True


def get_temp_dir():
    path = pathlib.Path(
        getattr(settings, 'RGD_TEMP_DIR', os.path.join(tempfile.gettempdir(), 'rgd'))
    )
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_cache_dir():
    path = pathlib.Path(get_temp_dir(), 'file_cache')
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_tilesource_from_image(
    image: Image, projection: str = None, style: str = None, encoding: str = 'PNG'
) -> FileTileSource:
    path = image.get_image_local_path()
    return large_image.open(str(path), projection=projection, style=style, encoding=encoding)


@contextmanager
def yeild_tilesource_from_image(image: Image, projection: str = None) -> FileTileSource:
    yield get_tilesource_from_image(image, projection)


def _get_region(tile_source: FileTileSource, region: dict, encoding: str):
    result, mime_type = tile_source.getRegion(region=region, encoding=encoding)
    if encoding == 'TILED':
        path = result
    else:
        # Write content to temporary file
        fd, path = tempfile.mkstemp(
            suffix=f'.{encoding}', prefix='pixelRegion_', dir=str(get_cache_dir())
        )
        os.close(fd)
        path = pathlib.Path(path)
        with open(path, 'wb') as f:
            f.write(result)
    return path, mime_type


def get_region(
    tile_source: FileTileSource,
    left: float,
    right: float,
    bottom: float,
    top: float,
    units: str = None,
    encoding: str = None,
):
    geospatial = hasattr(tile_source, 'geospatial') and tile_source.geospatial
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
        return _get_region(tile_source, region, encoding)
    units = 'pixels'
    left, right = min(left, right), max(left, right)
    top, bottom = min(top, bottom), max(top, bottom)
    region = dict(left=left, right=right, bottom=bottom, top=top, units=units)
    return _get_region(tile_source, region, encoding)


def get_tile_bounds(
    tile_source: FileTileSource,
    projection: str = 'EPSG:4326',
):
    bounds = tile_source.getBounds(srs=projection)
    threshold = 89.9999
    for key in ('ymin', 'ymax'):
        bounds[key] = max(min(bounds[key], threshold), -threshold)
    return bounds
