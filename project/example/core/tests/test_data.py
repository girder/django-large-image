import pytest


@pytest.mark.django_db(transaction=True)
def test_thumbnail(authenticated_api_client, image_file_geotiff):
    response = authenticated_api_client.get(f'/api/image-file/{image_file_geotiff.pk}/thumbnail')
    assert response.status_code == 200
    assert response['Content-Type'] == 'image/png'


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
def test_region_pixel(authenticated_api_client, image_file_geotiff, ome_image):
    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/region.tif?left=0&right=10&bottom=10&top=0&encoding=TILED&units=pixels'
    )
    assert response.status_code == 200
    assert response['Content-Type'] == 'image/tiff'
    response = authenticated_api_client.get(
        f'/api/image-file/{ome_image.pk}/region.tif?left=0&right=10&bottom=10&top=0&encoding=PNG&units=pixels'
    )
    assert response.status_code == 200
    assert response['Content-Type'] == 'image/png'


@pytest.mark.django_db(transaction=True)
def test_region_geo(authenticated_api_client, image_file_geotiff):
    response = authenticated_api_client.get(
        f'/api/image-file/{image_file_geotiff.pk}/region.tif?encoding=TILED&units=EPSG:4326&left=-117.4567824262003&right=-117.10373770277764&bottom=32.635234150046514&top=32.964410481130365'
    )
    assert response.status_code == 200
    assert response['Content-Type'] == 'image/tiff'
