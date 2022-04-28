from pathlib import Path

from django.contrib.auth.models import User
import pytest
from pytest_factoryboy import register
from rest_framework.test import APIClient

from myimages.imagefiles import models

from .factories import ImageFileFactory

register(ImageFileFactory)


@pytest.fixture
def api_client() -> APIClient:
    User.objects.create(username='admin', email='admin@kitware.com', password='password')
    return APIClient()


@pytest.fixture
def image_file_geotiff() -> models.ImageFile:
    return ImageFileFactory(
        file__filename='rgb_geotiff.tiff',
        file__from_path=Path(Path(__file__).parent, 'rgb_geotiff.tiff'),
    )
