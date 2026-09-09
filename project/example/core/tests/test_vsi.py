from unittest.mock import MagicMock, PropertyMock, patch

from django.core.files.storage import FileSystemStorage
from django.test import override_settings
import large_image.config
from large_image.tilesource.geo import make_vsi
import pytest
from rest_framework.exceptions import APIException

from django_large_image.apps import DjangoLargeImageConfig
from django_large_image.rest.viewsets import LargeImageVSIFileDetailMixin
from django_large_image.utilities import field_file_to_s3_url


@pytest.fixture
def force_gdal_vsis3_config():
    """Enable force_gdal_vsis3 for the duration of a test."""
    original = large_image.config.getConfig('force_gdal_vsis3')
    large_image.config.setConfig('force_gdal_vsis3', True)
    yield
    large_image.config.setConfig('force_gdal_vsis3', original)


@pytest.fixture
def disable_gdal_vsis3_config():
    """Disable force_gdal_vsis3 for the duration of a test."""
    original = large_image.config.getConfig('force_gdal_vsis3')
    large_image.config.setConfig('force_gdal_vsis3', False)
    yield
    large_image.config.setConfig('force_gdal_vsis3', original)


def test_make_vsi_s3_url():
    assert make_vsi('s3://bucket/key.tif') == '/vsis3/bucket/key.tif'


def test_make_vsi_http_uses_vsicurl_by_default(disable_gdal_vsis3_config):
    vsi = make_vsi('http://localhost:9000/bucket/key.tif')
    assert vsi.startswith('/vsicurl?')
    assert 'url=http%3A%2F%2Flocalhost%3A9000%2Fbucket%2Fkey.tif' in vsi


def test_make_vsi_https_uses_vsicurl_by_default(disable_gdal_vsis3_config):
    vsi = make_vsi('https://localhost:9000/bucket/key.tif')
    assert vsi.startswith('/vsicurl?')


def test_make_vsi_http_uses_vsis3_when_forced(force_gdal_vsis3_config):
    assert make_vsi('http://localhost:9000/bucket/key.tif') == '/vsis3/bucket/key.tif'


def test_make_vsi_https_uses_vsis3_when_forced(force_gdal_vsis3_config):
    assert make_vsi('https://localhost:9000/bucket/key.tif') == '/vsis3/bucket/key.tif'


def test_make_vsi_http_presigned_url_uses_path_only_when_forced(force_gdal_vsis3_config):
    url = (
        'http://localhost:9000/bucket/key.tif'
        '?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Signature=abc123'
    )
    assert make_vsi(url) == '/vsis3/bucket/key.tif'


MINIO_FILE_URL = 'http://localhost:9000/django-storage/rgb_geotiff.tiff'


@pytest.fixture
def restore_force_gdal_vsis3_config():
    original = large_image.config.getConfig('force_gdal_vsis3')
    yield
    large_image.config.setConfig('force_gdal_vsis3', original)


@override_settings(LARGE_IMAGE_FORCE_GDAL_VSIS3=True)
def test_make_vsi_http_uses_vsis3_from_django_setting(restore_force_gdal_vsis3_config):
    DjangoLargeImageConfig.create('django_large_image').ready()
    assert make_vsi(MINIO_FILE_URL) == '/vsis3/django-storage/rgb_geotiff.tiff'


@override_settings(LARGE_IMAGE_FORCE_GDAL_VSIS3=False)
def test_make_vsi_http_uses_vsicurl_from_django_setting(restore_force_gdal_vsis3_config):
    DjangoLargeImageConfig.create('django_large_image').ready()
    vsi = make_vsi(MINIO_FILE_URL)
    assert vsi.startswith('/vsicurl?')
    assert 'url=http%3A%2F%2Flocalhost%3A9000%2Fdjango-storage%2Frgb_geotiff.tiff' in vsi


def test_field_file_to_s3_url_minio():
    class FakeMinioStorage:
        bucket_name = 'django-storage'

    field_file = MagicMock()
    field_file.storage = FakeMinioStorage()
    field_file.name = 'path/to/rgb_geotiff.tiff'

    assert field_file_to_s3_url(field_file) == 's3://django-storage/path/to/rgb_geotiff.tiff'
    assert make_vsi(field_file_to_s3_url(field_file)) == (
        '/vsis3/django-storage/path/to/rgb_geotiff.tiff'
    )


def test_field_file_to_s3_url_django_storages():
    pytest.importorskip('storages')

    class FakeS3Storage:
        bucket_name = 'my-bucket'
        location = 'media'

    field_file = MagicMock()
    field_file.storage = FakeS3Storage()
    field_file.name = 'rgb_geotiff.tiff'

    assert field_file_to_s3_url(field_file) == 's3://my-bucket/media/rgb_geotiff.tiff'


def test_field_file_to_s3_url_unsupported_storage():
    field_file = MagicMock()
    field_file.storage = FileSystemStorage()
    field_file.name = 'local.tif'

    with pytest.raises(TypeError, match='MinIO or django-storages S3'):
        field_file_to_s3_url(field_file)


def test_vsi_mixin_uses_presigned_urls_by_default():
    mixin = LargeImageVSIFileDetailMixin()
    assert mixin.USE_PRESIGNED_URLS is True

    field_file = MagicMock()
    type(field_file).url = PropertyMock(
        return_value='http://localhost:9000/django-storage/rgb_geotiff.tiff'
    )

    with patch.object(mixin, 'get_field_file', return_value=field_file):
        with patch(
            'django_large_image.rest.viewsets.utilities.patch_internal_presign'
        ) as patch_presign:
            patch_presign.return_value.__enter__ = MagicMock(return_value=None)
            patch_presign.return_value.__exit__ = MagicMock(return_value=False)
            path = mixin.get_path(request=MagicMock(), pk=1)

    assert path.startswith('/vsicurl?') or path.startswith('/vsis3/')
    patch_presign.assert_called_once_with(field_file)


def test_vsi_mixin_uses_bucket_key_when_presigned_disabled():
    mixin = LargeImageVSIFileDetailMixin()
    mixin.USE_PRESIGNED_URLS = False

    field_file = MagicMock()
    with patch.object(mixin, 'get_field_file', return_value=field_file):
        with patch(
            'django_large_image.rest.viewsets.utilities.field_file_to_s3_url',
            return_value='s3://django-storage/rgb_geotiff.tiff',
        ) as to_s3:
            path = mixin.get_path(request=MagicMock(), pk=1)

    to_s3.assert_called_once_with(field_file)
    assert path == '/vsis3/django-storage/rgb_geotiff.tiff'


def test_vsi_mixin_bucket_key_raises_api_exception_for_bad_storage():
    mixin = LargeImageVSIFileDetailMixin()
    mixin.USE_PRESIGNED_URLS = False

    field_file = MagicMock()
    with patch.object(mixin, 'get_field_file', return_value=field_file):
        with patch(
            'django_large_image.rest.viewsets.utilities.field_file_to_s3_url',
            side_effect=TypeError('bad storage'),
        ):
            with pytest.raises(APIException, match='bad storage'):
                mixin.get_path(request=MagicMock(), pk=1)
