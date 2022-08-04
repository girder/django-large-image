import io

from PIL import Image
import pytest
from rest_framework import status

from django_large_image.tilesource import get_formats, get_mime_type


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('format', get_formats())
def test_thumbnail(authenticated_api_client, image_file_geotiff, format):
    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/data/thumbnail.{format}'
    )
    assert status.is_success(response.status_code)
    assert response['Content-Type'] == get_mime_type(format)


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('format', ['png', 'jpeg'])
def test_thumbnail_max_size(authenticated_api_client, image_file_geotiff, format):
    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/data/thumbnail.{format}?max_width=100'
    )
    assert status.is_success(response.status_code)
    assert response['Content-Type'] == f'image/{format}'
    # Check width of thumbnail
    with Image.open(io.BytesIO(response.content)) as im:
        assert im.width == 100

    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/data/thumbnail.{format}?max_height=100'
    )
    assert status.is_success(response.status_code)
    assert response['Content-Type'] == f'image/{format}'
    # Check height of thumbnail
    with Image.open(io.BytesIO(response.content)) as im:
        assert im.height == 100


@pytest.mark.django_db(transaction=True)
def test_histogram(authenticated_api_client, image_file_geotiff):
    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/data/histogram'
    )
    assert status.is_success(response.status_code)
    hist = response.data[0]
    assert isinstance(hist, dict)
    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/data/histogram?onlyMinMax=true'
    )
    assert status.is_success(response.status_code)
    assert 'min' in response.data


@pytest.mark.django_db(transaction=True)
def test_pixel(authenticated_api_client, image_file_geotiff):
    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/data/pixel?left=0&top=0'
    )
    assert status.is_success(response.status_code)
    data = response.data
    assert 'bands' in data


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('format', get_formats())
def test_region_pixel(authenticated_api_client, image_file_geotiff, ome_image, format):
    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/data/region.{format}?left=0&right=10&bottom=10&top=0&units=pixels'
    )
    assert status.is_success(response.status_code)
    assert response['Content-Type'] == get_mime_type(format)


@pytest.mark.django_db(transaction=True)
def test_region_pixel_out_of_bounds(authenticated_api_client, image_file_geotiff, ome_image):
    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/data/region.tif?left=10000000&right=20000000&bottom=20000000&top=10000000&units=pixels'
    )
    assert status.is_client_error(response.status_code)


@pytest.mark.django_db(transaction=True)
def test_region_geo(authenticated_api_client, image_file_geotiff):
    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/data/region.tif?units=EPSG:4326&left=-117.4567824262003&right=-117.10373770277764&bottom=32.635234150046514&top=32.964410481130365'
    )
    assert status.is_success(response.status_code)
    assert response['Content-Type'] == 'image/tiff'
    # Leave units out
    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/data/region.tif?left=-117.4567824262003&right=-117.10373770277764&bottom=32.635234150046514&top=32.964410481130365'
    )
    assert status.is_success(response.status_code)
    assert response['Content-Type'] == 'image/tiff'
