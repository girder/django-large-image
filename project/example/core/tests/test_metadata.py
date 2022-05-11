import pytest
from rest_framework import status


@pytest.mark.django_db(transaction=True)
def test_metadata(authenticated_api_client, image_file_geotiff):
    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/metadata?projection=EPSG:3857'
    )
    assert status.is_success(response.status_code)
    metadata = response.data
    assert metadata['geospatial']
    assert metadata['levels'] == 9
    assert metadata['sizeX'] == metadata['sizeY']
    assert metadata['tileWidth'] == metadata['tileHeight']
    assert metadata['tileWidth'] == metadata['tileHeight']


@pytest.mark.django_db(transaction=True)
def test_metadata_vsi(authenticated_api_client, image_file_geotiff):
    response = authenticated_api_client.get(
        f'/api/vsi-image-file/{image_file_geotiff.pk}/metadata?projection=EPSG:3857'
    )
    assert status.is_success(response.status_code)
    metadata = response.data
    assert metadata['geospatial']
    assert metadata['levels'] == 9
    assert metadata['sizeX'] == metadata['sizeY']
    assert metadata['tileWidth'] == metadata['tileHeight']
    assert metadata['tileWidth'] == metadata['tileHeight']


@pytest.mark.django_db(transaction=True)
def test_metadata_s3(authenticated_api_client, s3_image_file_geotiff):
    response = authenticated_api_client.get(
        f'/api/s3-image-file/{s3_image_file_geotiff.pk}/metadata?projection=EPSG:3857'
    )
    assert status.is_success(response.status_code)
    metadata = response.data
    assert metadata['geospatial']
    assert metadata['levels'] == 9
    assert metadata['sizeX'] == metadata['sizeY']
    assert metadata['tileWidth'] == metadata['tileHeight']
    assert metadata['tileWidth'] == metadata['tileHeight']


@pytest.mark.django_db(transaction=True)
def test_metadata_s3_vsi(authenticated_api_client, s3_image_file_geotiff):
    response = authenticated_api_client.get(
        f'/api/s3-vsi-image-file/{s3_image_file_geotiff.pk}/metadata?projection=EPSG:3857'
    )
    assert status.is_success(response.status_code)
    metadata = response.data
    assert metadata['geospatial']
    assert metadata['levels'] == 9
    assert metadata['sizeX'] == metadata['sizeY']
    assert metadata['tileWidth'] == metadata['tileHeight']
    assert metadata['tileWidth'] == metadata['tileHeight']


@pytest.mark.django_db(transaction=True)
def test_metadata_internal(authenticated_api_client, image_file_geotiff):
    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/metadata_internal'
    )
    assert status.is_success(response.status_code)
    metadata = response.data
    assert metadata['geospatial']
    assert metadata['driverLongName']


@pytest.mark.django_db(transaction=True)
def test_bands(authenticated_api_client, image_file_geotiff):
    response = authenticated_api_client.get(f'/api/image-file/{image_file_geotiff.pk}/bands')
    assert status.is_success(response.status_code)
    bands = response.data
    assert isinstance(bands[1], dict)


@pytest.mark.django_db(transaction=True)
def test_frames(authenticated_api_client, image_file_geotiff):
    response = authenticated_api_client.get(f'/api/image-file/{image_file_geotiff.pk}/frames')
    assert status.is_success(response.status_code)
    data = response.data
    assert isinstance(data['frames'], list)
    assert isinstance(data['frames'][0], dict)
    assert 'bands' in data['frames'][0]


@pytest.mark.django_db(transaction=True)
def test_band(authenticated_api_client, image_file_geotiff):
    response = authenticated_api_client.get(f'/api/image-file/{image_file_geotiff.pk}/band?band=1')
    assert status.is_success(response.status_code)
    band = response.data
    assert band['interpretation']


@pytest.mark.django_db(transaction=True)
def test_metadata_ome(authenticated_api_client, ome_image):
    response = authenticated_api_client.get(
        f'/api/image-file/{ome_image.pk}/metadata?source=ometiff'
    )
    assert status.is_success(response.status_code)
    metadata = response.data
    assert 'frames' in metadata
    assert len(metadata['frames'])
    assert not metadata['geospatial']
    assert metadata['sizeX'] == metadata['sizeY']
    assert metadata['tileWidth'] == metadata['tileHeight']
    assert metadata['tileWidth'] == metadata['tileHeight']


@pytest.mark.django_db(transaction=True)
def test_bad_source(authenticated_api_client, image_file_geotiff):
    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/metadata?source=foo'
    )
    assert status.is_client_error(response.status_code)


@pytest.mark.django_db(transaction=True)
def test_bad_image_data(authenticated_api_client, lonely_header_file):
    # Catches server error safely and returns 500-level APIException
    response = authenticated_api_client.get(f'/api/image-file/{lonely_header_file.pk}/metadata')
    assert status.is_server_error(response.status_code)


@pytest.mark.django_db(transaction=True)
def test_tiffdump(authenticated_api_client, s3_image_file_geotiff, png_image):
    response = authenticated_api_client.get(
        f'/api/s3-image-file/{s3_image_file_geotiff.pk}/tiffdump'
    )
    assert status.is_success(response.status_code)
    dump = response.data
    assert 'firstifd' in dump
    assert 'size' in dump
    assert dump['ifds']

    # Server error raised when image isn't accessible locally
    response = authenticated_api_client.get(
        f'/api/s3-vsi-image-file/{s3_image_file_geotiff.pk}/tiffdump'
    )
    assert status.is_server_error(response.status_code)

    # Client error raised when image is not a tiff
    response = authenticated_api_client.get(f'/api/image-file/{png_image.pk}/tiffdump')
    assert status.is_client_error(response.status_code)
