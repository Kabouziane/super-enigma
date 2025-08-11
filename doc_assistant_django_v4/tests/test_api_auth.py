import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
@pytest.mark.django_db
def test_token_obtain_and_protected_endpoints(client):
    u = User.objects.create_user('testuser', password='pass123')
    c = APIClient()
    # obtain token (using simplejwt endpoint provided by urls)
    resp = c.post('/api/token/', {'username':'testuser','password':'pass123'}, format='json')
    assert resp.status_code == 200
    data = resp.json()
    assert 'access' in data
    token = data['access']
    c.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    # call protected upload endpoint without file -> should return 400 (we are authenticated)
    resp2 = c.post('/upload/', {}, format='multipart')
    assert resp2.status_code in (400,415)
