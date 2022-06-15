import pytest
from rest_framework import status


@pytest.mark.django_db(transaction=True)
def test_metadata(api_client, image_file_geotiff):
    response = api_client.get(
        f'/api/imagefile/{image_file_geotiff.pk}/info/metadata?projection=EPSG:3857'
    )
    assert status.is_success(response.status_code)
    metadata = response.data
    assert metadata['geospatial']
    assert metadata['levels'] == 9
    assert metadata['sizeX'] == metadata['sizeY']
    assert metadata['tileWidth'] == metadata['tileHeight']
    assert metadata['tileWidth'] == metadata['tileHeight']


@pytest.mark.django_db(transaction=True)
def test_metadata_internal(api_client, image_file_geotiff):
    response = api_client.get(f'/api/imagefile/{image_file_geotiff.pk}/info/metadata_internal')
    assert status.is_success(response.status_code)
    metadata = response.data
    assert metadata['geospatial']
    assert metadata['driverLongName']


@pytest.mark.django_db(transaction=True)
def test_bands(api_client, image_file_geotiff):
    response = api_client.get(f'/api/imagefile/{image_file_geotiff.pk}/info/bands')
    assert status.is_success(response.status_code)
    bands = response.data
    assert isinstance(bands[1], dict)


@pytest.mark.django_db(transaction=True)
def test_frames(api_client, image_file_geotiff):
    response = api_client.get(f'/api/imagefile/{image_file_geotiff.pk}/info/frames')
    assert status.is_success(response.status_code)
    data = response.data
    assert isinstance(data['frames'], list)
    assert isinstance(data['frames'][0], dict)
    assert 'bands' in data['frames'][0]


@pytest.mark.django_db(transaction=True)
def test_band(api_client, image_file_geotiff):
    response = api_client.get(f'/api/imagefile/{image_file_geotiff.pk}/info/band?band=1')
    assert status.is_success(response.status_code)
    band = response.data
    assert band['interpretation']
