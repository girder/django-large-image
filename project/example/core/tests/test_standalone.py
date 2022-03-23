import pytest
from rest_framework import status


@pytest.mark.django_db(transaction=True)
def test_swagger(authenticated_api_client):
    response = authenticated_api_client.get('/swagger/?format=openapi')
    assert status.is_success(response.status_code)


@pytest.mark.django_db(transaction=True)
def test_list_sources(authenticated_api_client):
    response = authenticated_api_client.get('/api/large-image/sources')
    assert status.is_success(response.status_code)


@pytest.mark.django_db(transaction=True)
def test_list_colormaps(authenticated_api_client):
    response = authenticated_api_client.get('/api/large-image/colormaps')
    assert status.is_success(response.status_code)
