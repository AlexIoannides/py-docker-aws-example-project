"""
test_microservice.py
~~~~~~~~~~~~~~~~~~~~

Tests the the service returns the expected responses .
"""

import json
import unittest

from microservice.api import app


class TestMicroserviceAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
 
    def test_service(self):
        """Test endpoint mesage"""

        # arrange
        uri = '/microservice'

        # act
        response = self.client.get(uri)

        # assert
        exp_response = {
            'health_check': 'The microservice is operational.'}
        
        self.assertEqual(response.json, exp_response)


if __name__ == '__main__':
    unittest.main()