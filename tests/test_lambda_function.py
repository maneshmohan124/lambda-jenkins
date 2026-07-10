"""Unit tests for the Hello World Lambda function."""

import json
import unittest

from lambda_function import lambda_handler


class TestLambdaHandler(unittest.TestCase):
    """Test cases for lambda_handler."""

    def test_default_greeting(self):
        """When no name is provided, respond with 'Hello, World!'."""
        event = {}
        context = None
        response = lambda_handler(event, context)

        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["message"], "Hello, World!")

    def test_custom_greeting(self):
        """When a name is provided, respond with a personalised greeting."""
        event = {"name": "Jenkins"}
        context = None
        response = lambda_handler(event, context)

        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["message"], "Hello, Jenkins!")

    def test_response_headers(self):
        """Response should include JSON content-type header."""
        response = lambda_handler({}, None)
        self.assertEqual(response["headers"]["Content-Type"], "application/json")


if __name__ == "__main__":
    unittest.main()
