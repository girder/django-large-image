from contextlib import contextmanager
import os
import pathlib
import shutil
import tempfile
from typing import Any
from urllib.parse import urlencode

from django.conf import settings
from django.core.files import File
from django.db.models.fields.files import FieldFile
import large_image
from large_image.tilesource import FileTileSource

try:
    from minio_storage.storage import MinioStorage
except ImportError:
    MinioStorage = None


@contextmanager
def patch_internal_presign(f: FieldFile):
    """Create an environment where Minio-based `FieldFile`s construct a locally accessible presigned URL.

    Sometimes the external host differs from the internal host for Minio files (e.g. in development).
    Getting the URL in this context ensures that the presigned URL returns the correct host for the
    odd situation of accessing the file locally.

    Note
    ----
    If concerned regarding concurrent access, see https://github.com/ResonantGeoData/ResonantGeoData/issues/287

    """
    if (
        MinioStorage is not None
        and isinstance(f.storage, MinioStorage)
        and getattr(settings, 'MINIO_STORAGE_MEDIA_URL', None) is not None
    ):
        original_base_url = f.storage.base_url
        try:
            f.storage.base_url = None
            yield
        finally:
            f.storage.base_url = original_base_url
        return
    yield


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


def make_vsi(url: str, **options):
    if str(url).startswith('s3://'):
        s3_path = url.replace('s3://', '')
        vsi = f'/vsis3/{s3_path}'
    else:
        gdal_options = {
            'url': str(url),
            'use_head': 'no',
            'list_dir': 'no',
        }
        gdal_options.update(options)
        vsi = f'/vsicurl?{urlencode(gdal_options)}'
    return vsi


def field_file_to_local_path(field_file: FieldFile) -> pathlib.Path:
    """Download entire FieldFile to disk location.

    This overrides `girder_utils.field_file_to_local_path` to download file to
    local path without a context manager. Cleanup must be handled by caller.

    """
    field_file_basename = pathlib.PurePath(field_file.name).name
    directory = get_cache_dir() / f'{type(field_file.instance).__name__}-{field_file.instance.pk}'
    dest_path = directory / field_file_basename

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with field_file.open('rb'):
        file_obj: File = field_file.file
        if type(file_obj) is File:
            # When file_obj is an actual File, (typically backed by FileSystemStorage),
            # it is already at a stable path on disk.
            # We must symlink it into the desired path
            os.symlink(file_obj.name, dest_path)
            return dest_path
        else:
            # When file_obj is actually a subclass of File, it only provides a Python
            # file-like object API. So, it must be copied to a stable path.
            if dest_path.exists():
                # WARNING: this is probably not thread safe
                #  S3FF is fundamentally incompatible with tile serving
                return dest_path
            with open(dest_path, 'wb') as dest_stream:
                shutil.copyfileobj(file_obj, dest_stream)
                dest_stream.flush()
            return dest_path


def get_or_create_no_commit(model: Any, defaults: dict = None, **kwargs):
    try:
        return model.objects.get(**kwargs), False
    except model.DoesNotExist:
        if not defaults:
            defaults = {}
        defaults.update(kwargs)
        return model(**defaults), True


def get_tilesource_from_image(
    path: str, projection: str = None, style: str = None, encoding: str = 'PNG'
) -> FileTileSource:
    return large_image.open(str(path), projection=projection, style=style, encoding=encoding)


@contextmanager
def yeild_tilesource_from_image(path: str, projection: str = None) -> FileTileSource:
    yield get_tilesource_from_image(path, projection)


def is_geospatial(tile_source: FileTileSource):
    return tile_source.getMetadata().get('geospatial', False)


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
    if not bounds:
        return
    threshold = 89.9999
    for key in ('ymin', 'ymax'):
        bounds[key] = max(min(bounds[key], threshold), -threshold)
    return bounds
