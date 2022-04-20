import io

from PIL import Image
import pytest


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('format', ['png', 'jpeg'])
def test_thumbnail(authenticated_api_client, image_file_geotiff, format):
    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/thumbnail.{format}'
    )
    assert response.status_code == 200
    assert response['Content-Type'] == f'image/{format}'


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('format', ['png', 'jpeg'])
def test_thumbnail_max_size(authenticated_api_client, image_file_geotiff, format):
    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/thumbnail.{format}?max_width=100'
    )
    assert response.status_code == 200
    assert response['Content-Type'] == f'image/{format}'
    # Check width of thumbnail
    with Image.open(io.BytesIO(response.content)) as im:
        assert im.width == 100

    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/thumbnail.{format}?max_height=100'
    )
    assert response.status_code == 200
    assert response['Content-Type'] == f'image/{format}'
    # Check height of thumbnail
    with Image.open(io.BytesIO(response.content)) as im:
        assert im.height == 100


@pytest.mark.django_db(transaction=True)
def test_histogram(authenticated_api_client, image_file_geotiff):
    response = authenticated_api_client.get(f'/api/image-file/{image_file_geotiff.pk}/histogram')
    assert response.status_code == 200
    hist = response.data[0]
    assert isinstance(hist, dict)


@pytest.mark.django_db(transaction=True)
def test_pixel(authenticated_api_client, image_file_geotiff):
    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/pixel?left=0&top=0'
    )
    assert response.status_code == 200
    data = response.data
    assert 'bands' in data


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('format', ['png', 'jpeg', 'tif'])
def test_region_pixel(authenticated_api_client, image_file_geotiff, ome_image, format):
    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/region.{format}?left=0&right=10&bottom=10&top=0&units=pixels'
    )
    assert response.status_code == 200
    if format == 'tif':
        format = 'tiff'  # Change for mime_type
    assert response['Content-Type'] == f'image/{format}'


@pytest.mark.django_db(transaction=True)
def test_region_pixel_out_of_bounds(authenticated_api_client, image_file_geotiff, ome_image):
    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/region.tif?left=10000000&right=20000000&bottom=20000000&top=10000000&units=pixels'
    )
    assert response.status_code == 400


@pytest.mark.django_db(transaction=True)
def test_region_geo(authenticated_api_client, image_file_geotiff):
    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/region.tif?units=EPSG:4326&left=-117.4567824262003&right=-117.10373770277764&bottom=32.635234150046514&top=32.964410481130365'
    )
    assert response.status_code == 200
    assert response['Content-Type'] == 'image/tiff'
