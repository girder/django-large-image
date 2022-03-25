from contextlib import contextmanager
import logging
import os
import pathlib
import shutil
import tempfile
from urllib.parse import urlencode

from django.conf import settings
from django.core.files import File
from django.db.models.fields.files import FieldFile

try:
    from minio_storage.storage import MinioStorage
except ImportError:
    MinioStorage = None

logger = logging.getLogger(__name__)


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
        if f.storage.base_url is not None:
            try:
                f.storage.base_url = None
                yield
            finally:
                f.storage.base_url = original_base_url
            return
    yield


def get_temp_dir():
    path = pathlib.Path(
        getattr(
            settings, 'DATA_TEMP_DIR', os.path.join(tempfile.gettempdir(), 'django-large-image')
        )
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
            logger.debug('Performing symlink')
            return dest_path
        else:
            # When file_obj is actually a subclass of File, it only provides a Python
            # file-like object API. So, it must be copied to a stable path.
            logger.debug('copying file...')
            if dest_path.exists():
                # WARNING: this is probably not thread safe
                #  S3FF is fundamentally incompatible with tile serving
                logger.debug('...Found existing')
                return dest_path
            with open(dest_path, 'wb') as dest_stream:
                shutil.copyfileobj(file_obj, dest_stream)
                dest_stream.flush()
            return dest_path
