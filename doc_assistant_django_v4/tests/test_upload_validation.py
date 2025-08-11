import pytest, io
from django.contrib.auth.models import User
from rest_framework.test import APIClient
@pytest.mark.django_db
def test_upload_rejects_non_pdf(tmp_path):
    u = User.objects.create_user('t','t@t',password='p')
    c = APIClient()
    resp = c.post('/api/token/', {'username':'t','password':'p'}, format='json')
    token = resp.json()['access']
    c.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    fake = io.BytesIO(b'NOTPDFDATA')
    fake.name = 'bad.txt'
    resp2 = c.post('/upload/', {'file': fake}, format='multipart')
    assert resp2.status_code == 400
