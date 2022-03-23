import pytest


@pytest.mark.django_db(transaction=True)
def test_thumbnail(authenticated_api_client, image_file_geotiff):
    response = authenticated_api_client.get(f'/api/large-image/{image_file_geotiff.pk}/thumbnail')
    assert response.status_code == 200
    assert response['Content-Type'] == 'image/png'


@pytest.mark.django_db(transaction=True)
def test_histogram(authenticated_api_client, image_file_geotiff):
    response = authenticated_api_client.get(f'/api/large-image/{image_file_geotiff.pk}/histogram')
    assert response.status_code == 200
    hist = response.data[0]
    assert isinstance(hist, dict)


@pytest.mark.django_db(transaction=True)
def test_pixel(authenticated_api_client, image_file_geotiff):
    response = authenticated_api_client.get(f'/api/large-image/{image_file_geotiff.pk}/pixel/0/0')
    assert response.status_code == 200
    data = response.data
    assert 'bands' in data
