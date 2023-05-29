import pytest
from rest_framework import status

from django_large_image.tilesource import get_formats, get_mime_type


@pytest.mark.django_db(transaction=True)
def test_tile(authenticated_api_client, image_file_geotiff):
    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/tiles/1/0/0.png?projection=EPSG:3857'
    )
    assert status.is_success(response.status_code)
    assert response['Content-Type'] == 'image/png'
    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/tiles/1/0/0.jpeg?projection=EPSG:3857'
    )
    assert status.is_success(response.status_code)
    assert response['Content-Type'] == 'image/jpeg'
    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/tiles/100/0/0.png'
    )
    assert status.is_client_error(response.status_code)


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('format', get_formats())
def test_tile_formats(authenticated_api_client, image_file_geotiff, format):
    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/tiles/1/0/0.{format}?projection=EPSG:3857'
    )
    assert status.is_success(response.status_code)
    assert response['Content-Type'] == get_mime_type(format)


@pytest.mark.django_db(transaction=True)
def test_tile_corners(authenticated_api_client, image_file_geotiff):
    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/tiles/1/0/0/corners?projection=EPSG:3857'
    )
    assert status.is_success(response.status_code)
    data = response.data
    assert 'xmin' in data
    assert 'xmax' in data
    assert 'ymin' in data
    assert 'ymax' in data


@pytest.mark.django_db(transaction=True)
def test_tiles_metadata(authenticated_api_client, image_file_geotiff):
    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/tiles/metadata?projection=EPSG:3857'
    )
    assert status.is_success(response.status_code)
    metadata = response.data
    assert metadata['geospatial']
    assert metadata['levels'] == 9
    assert metadata['size_x'] == metadata['size_x']
    assert metadata['additional_metadata']
    assert (
        metadata['additional_metadata']['tileWidth']
        == metadata['additional_metadata']['tileHeight']
    )
    assert (
        metadata['additional_metadata']['tileWidth']
        == metadata['additional_metadata']['tileHeight']
    )


@pytest.mark.django_db(transaction=True)
def test_non_geo_tiles(authenticated_api_client, png_image):
    response = authenticated_api_client.get(f'/api/image-file/{png_image.pk}/tiles/0/0/0.png')
    assert status.is_success(response.status_code)
    assert response['Content-Type'] == 'image/png'


@pytest.mark.django_db(transaction=True)
def test_ome_tiles(authenticated_api_client, ome_image):
    response = authenticated_api_client.get(f'/api/image-file/{ome_image.pk}/tiles/0/0/0.png')
    assert status.is_success(response.status_code)
    assert response['Content-Type'] == 'image/png'
    response = authenticated_api_client.get(
        f'/api/image-file/{ome_image.pk}/tiles/0/0/0.png?source=ometiff'
    )
    assert status.is_success(response.status_code)
    assert response['Content-Type'] == 'image/png'
