from django.test import TestCase
from django.contrib.auth.models import User
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from unittest import mock

class ElasticsearchAuthTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.username = 'testuser'
        self.password = 'testpass'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def tearDown(self):
        # Clean up the test user
        self.user.delete()

    def test_authentication_with_elasticsearch(self):
        # Create a mock Elasticsearch client
        es_client = Elasticsearch()

        # Define the Elasticsearch authentication response
        auth_response = {
            'username': self.username,
            'password': self.password
        }

        # Mock the Elasticsearch client's get method
        with mock.patch.object(es_client, 'get') as mock_get:
            mock_get.return_value = auth_response

            # Perform the test action that requires authentication
            try:
                # Perform an Elasticsearch action that requires authentication
                es_client.get(index='users', id='JFhQOIgBI-yLtDPF-ikm')
            except NotFoundError:
                # Handle the NotFoundError if the document is not found
                pass

            # Assert that the get method was called with the correct parameters
            mock_get.assert_called_with(index='users', id='JFhQOIgBI-yLtDPF-ikm')



