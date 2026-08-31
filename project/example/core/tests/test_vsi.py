from django.test import override_settings
import large_image.config
from large_image.tilesource.geo import make_vsi
import pytest

from django_large_image.apps import DjangoLargeImageConfig


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
