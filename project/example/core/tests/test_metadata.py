import pytest


@pytest.mark.django_db(transaction=True)
def test_metadata(authenticated_api_client, image_file_geotiff):
    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/metadata?projection=EPSG:3857'
    )
    assert response.status_code == 200
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
    assert response.status_code == 200
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
    assert response.status_code == 200
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
    assert response.status_code == 200
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
    assert response.status_code == 200
    metadata = response.data
    assert metadata['geospatial']
    assert metadata['driverLongName']


@pytest.mark.django_db(transaction=True)
def test_bands(authenticated_api_client, image_file_geotiff):
    response = authenticated_api_client.get(f'/api/image-file/{image_file_geotiff.pk}/bands')
    assert response.status_code == 200
    bands = response.data
    assert isinstance(bands[1], dict)


@pytest.mark.django_db(transaction=True)
def test_band(authenticated_api_client, image_file_geotiff):
    response = authenticated_api_client.get(f'/api/image-file/{image_file_geotiff.pk}/band?band=1')
    assert response.status_code == 200
    band = response.data
    assert band['interpretation']


@pytest.mark.django_db(transaction=True)
def test_metadata_ome(authenticated_api_client, ome_image):
    response = authenticated_api_client.get(
        f'/api/image-file/{ome_image.pk}/metadata?source=ometiff'
    )
    assert response.status_code == 200
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
    assert response.status_code == 400
