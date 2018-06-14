from django.test import TestCase
from django.contrib.auth.models import User

from auth.models import Client
from auth.views import UserViewSet

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import force_authenticate
from rest_framework.test import APIRequestFactory

# Create your tests here.

class ClientKeyAndSecretGenerationTest(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()

    def test_client_creation_without_providing_values(self):
        request = self.factory.post('/auth/signup/')
        response = UserViewSet.as_view({'post':'create'})(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['username'], [u'This field is required.'])
        self.assertEqual(response.data['password'], [u'This field is required.'])

    def test_client_creation_when_providing_values(self):
        request = self.factory.post('/auth/signup/', {'username':'anubhav722', 'password':'password123',
                                                    'email':'anubhav722@gmail.com'})
        response = UserViewSet.as_view({'post':'create'})(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['Client Key']), 40)
        self.assertEqual(len(response.data['Client Secret']), 64)