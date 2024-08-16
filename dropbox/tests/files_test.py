import unittest
import json
import os
from unittest.mock import patch, MagicMock
from dropbox.services.files import get_images

url = "https://api.dropboxapi.com/2/files/list_folder"
class TestGetImages(unittest.TestCase):
    
    @patch('requests.post')
    def test_get_images_success(self, mock_post):
        # Mock the response from requests.post
        mock_response = MagicMock()
        mock_response.json.return_value = {"entries": ["image1.jpg", "image2.jpg"]}
        mock_post.return_value = mock_response

        # Run the function
        result = get_images()

        # Check that requests.post was called with the correct parameters
        expected_headers = {
            "Authorization": "Bearer " + os.getenv('DROPBOX_TOKEN'),
            "Content-Type": "application/json"
        }
        expected_data = json.dumps({"path": ""})

        mock_post.assert_called_once_with(url, headers=expected_headers, data=expected_data)

        # Check the result
        self.assertEqual(result, {"entries": ["image1.jpg", "image2.jpg"]})

    @patch('requests.post')
    def test_get_images_failure(self, mock_post):
        # Mock the response from requests.post
        mock_response = MagicMock()
        mock_response.json.return_value = {"error": "Something went wrong"}
        mock_post.return_value = mock_response

        # Run the function
        result = get_images()

        # Check that requests.post was called with the correct parameters
        expected_headers = {
            "Authorization": "Bearer " + os.getenv('DROPBOX_TOKEN'),
            "Content-Type": "application/json"
        }
        expected_data = json.dumps({"path": ""})

        mock_post.assert_called_once_with(url, headers=expected_headers, data=expected_data)

        # Check the result
        self.assertEqual(result, {"error": "Something went wrong"})


if __name__ == '__main__':
    unittest.main()