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
from filelock import FileLock

try:
    from minio_storage.storage import MinioStorage  # pragma: no cover
except ImportError:  # pragma: no cover
    MinioStorage = None

logger = logging.getLogger(__name__)


def param_nully(value) -> bool:
    """Determine null-like values."""
    if isinstance(value, str):
        value = value.lower()
    return value in [None, '', 'undefined', 'none', 'null', 'false']


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


def get_temp_dir() -> pathlib.Path:
    path = pathlib.Path(
        getattr(
            settings, 'DATA_TEMP_DIR', os.path.join(tempfile.gettempdir(), 'django-large-image')
        )
    )
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_cache_dir() -> pathlib.Path:
    path = pathlib.Path(get_temp_dir(), 'file_cache')
    path.mkdir(parents=True, exist_ok=True)
    return path


def make_vsi(url: str, **options) -> str:
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


def get_lock_dir() -> pathlib.Path:
    path = pathlib.Path(get_temp_dir(), 'file_locks')
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_lock(path: pathlib.Path) -> FileLock:
    """Create a file lock under the lock directory."""
    # Computes the hash using Pathlib's hash implementation on absolute path
    sha = hash(path.absolute())
    lock_path = pathlib.Path(get_lock_dir(), f'{sha}.lock')
    lock = FileLock(str(lock_path))
    return lock


def get_file_safe_path(path: pathlib.Path) -> pathlib.Path:
    """Mark the file/lock as safe to use."""
    sha = hash(path.absolute())
    return pathlib.Path(get_lock_dir(), f'{sha}.safe')


def field_file_to_local_path(field_file: FieldFile) -> pathlib.Path:
    """Download entire FieldFile to disk location.

    This overrides `girder_utils.field_file_to_local_path` to download file to
    local path without a context manager. Cleanup must be handled by caller.

    This puts a file lock on the file to prevent concurrent access while
    downloading.

    """
    field_file_basename = pathlib.PurePath(field_file.name).name
    directory = get_cache_dir() / f'{type(field_file.instance).__name__}-{field_file.instance.pk}'
    dest_path = directory / field_file_basename

    lock = get_file_lock(dest_path)
    safe = get_file_safe_path(dest_path)

    with lock.acquire():
        if not safe.exists():
            # file doesn't yet exist (or is corrupt) and we need to download it
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with field_file.open('rb'):
                file_obj: File = field_file.file
                if type(file_obj) is File:
                    # When file_obj is an actual File, (typically backed by FileSystemStorage),
                    # it is already at a stable path on disk.
                    # We must symlink it into the desired path
                    os.symlink(file_obj.name, dest_path)
                    logger.debug('Performing symlink')
                else:
                    # When file_obj is actually a subclass of File, it only provides a Python
                    # file-like object API. So, it must be copied to a stable path.
                    logger.debug('copying file...')
                    with open(dest_path, 'wb') as dest_stream:
                        shutil.copyfileobj(file_obj, dest_stream)
                        dest_stream.flush()
            # Mark file as safe
            logger.debug('Marking as safely downloaded...')
            safe.touch()
    return dest_path
