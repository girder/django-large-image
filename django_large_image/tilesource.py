"""large-image utilities."""
import os
import pathlib
import tempfile
from typing import List

import large_image
from large_image.tilesource import FileTileSource
from rest_framework.exceptions import ValidationError

from django_large_image import utilities


def get_tilesource_from_path(
    path: str, projection: str = None, style: str = None, encoding: str = None
) -> FileTileSource:
    if encoding is None:
        encoding = 'PNG'
    return large_image.open(str(path), projection=projection, style=style, encoding=encoding)


def is_geospatial(source: FileTileSource) -> bool:
    return source.getMetadata().get('geospatial', False)


def get_bounds(
    source: FileTileSource,
    projection: str = 'EPSG:4326',
) -> List[float]:
    bounds = source.getBounds(srs=projection)
    if not bounds:
        return
    threshold = 89.9999
    for key in ('ymin', 'ymax'):
        bounds[key] = max(min(bounds[key], threshold), -threshold)
    return bounds


def _metadata_helper(source: FileTileSource, metadata: dict):
    metadata.setdefault('geospatial', is_geospatial(source))
    if metadata['geospatial']:
        metadata['bounds'] = get_bounds(source)
        metadata['proj4'] = (source.getProj4String(),)
    if 'frames' not in metadata:
        metadata['frames'] = False


def get_metadata(source: FileTileSource) -> dict:
    metadata = source.getMetadata()
    _metadata_helper(source, metadata)
    return metadata


def get_metadata_internal(source: FileTileSource) -> dict:
    metadata = source.getInternalMetadata()
    _metadata_helper(source, metadata)
    return metadata


def _get_region(source: FileTileSource, region: dict, encoding: str) -> (pathlib.Path, str):
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
) -> (pathlib.Path, str):
    if isinstance(units, str):
        units = units.lower()
    if encoding is None and is_geospatial(source):
        # Use tiled encoding by default for geospatial rasters
        #   output will be a tiled TIF
        encoding = 'TILED'
    elif encoding is None:
        # Use JPEG encoding by default for nongeospatial rasters
        encoding = 'JPEG'
    if is_geospatial(source) and units not in [
        'pixels',
        'pixel',
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


def format_to_encoding(format: str) -> str:
    """Translate format extension (e.g., `tiff`) to encoding (e.g., `TILED`)."""
    if format is None:
        return 'PNG'
    if format.lower() not in ['tif', 'tiff', 'png', 'jpeg', 'jpg']:
        raise ValidationError(f'Format `{format}` is not valid. Try `png`, `jpeg`, or `tif`')
    if format.lower() in ['tif', 'tiff']:
        return 'TILED'
    return format.upper()  # jpeg, png
