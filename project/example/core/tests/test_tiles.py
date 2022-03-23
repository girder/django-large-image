import pytest
from rest_framework import status


@pytest.mark.django_db(transaction=True)
def test_swagger(authenticated_api_client):
    response = authenticated_api_client.get('/swagger/?format=openapi')
    assert status.is_success(response.status_code)


@pytest.mark.django_db(transaction=True)
def test_metadata(authenticated_api_client, image_file_geotiff):
    response = authenticated_api_client.get(
        f'/api/large-image/{image_file_geotiff.pk}/metadata?projection=EPSG:3857'
    )
    metadata = response.data
    assert metadata['levels'] == 9
    assert metadata['sizeX'] == metadata['sizeY']
    assert metadata['tileWidth'] == metadata['tileHeight']
    assert metadata['tileWidth'] == metadata['tileHeight']


@pytest.mark.django_db(transaction=True)
def test_tile(authenticated_api_client, image_file_geotiff):
    response = authenticated_api_client.get(
        f'/api/large-image/{image_file_geotiff.pk}/tiles/1/0/0.png'
    )
    assert response.status_code == 200
    assert response['Content-Type'] == 'image/png'


@pytest.mark.django_db(transaction=True)
def test_thumbnail(authenticated_api_client, image_file_geotiff):
    response = authenticated_api_client.get(f'/api/large-image/{image_file_geotiff.pk}/thumbnail')
    assert response.status_code == 200
    assert response['Content-Type'] == 'image/png'


# @pytest.mark.django_db(transaction=True)
# def test_cache(authenticated_api_client, image_file_geotiff, django_assert_num_queries):
#     # cache a response
#     authenticated_api_client.get(f'/api/large-image/{image_file_geotiff.pk}/tiles/1/0/0.png')
#     # ensure no new queries are made for a different tile request made by same user on same image
#     with django_assert_num_queries(0):
#         authenticated_api_client.get(f'/api/large-image/{image_file_geotiff.pk}/tiles/1/1/0.png')


@pytest.mark.django_db(transaction=True)
def test_non_geo_tiles(authenticated_api_client, non_geo_image):
    response = authenticated_api_client.get(f'/api/large-image/{non_geo_image.pk}/tiles/0/0/0.png')
    assert response.status_code == 200
    assert response['Content-Type'] == 'image/png'
