from example.core import models
from example.core.datastore import datastore
import pytest
from pytest_factoryboy import register
from rest_framework.test import APIClient

from .factories import ImageFileFactory, S3ImageFileFactory, UserFactory

register(UserFactory)
register(ImageFileFactory)
register(S3ImageFileFactory)


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def authenticated_api_client(user) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def image_file_geotiff() -> models.ImageFile:
    return ImageFileFactory(
        file__filename='rgb_geotiff.tiff',
        file__from_path=datastore.fetch('rgb_geotiff.tiff'),
    )


@pytest.fixture
def s3_image_file_geotiff() -> models.S3ImageFile:
    return S3ImageFileFactory(
        file__filename='rgb_geotiff.tiff',
        file__from_path=datastore.fetch('rgb_geotiff.tiff'),
    )


@pytest.fixture
def non_geo_image() -> models.ImageFile:
    return ImageFileFactory(
        file__filename='afie_1.jpg',
        file__from_path=datastore.fetch('afie_1.jpg'),
    )
