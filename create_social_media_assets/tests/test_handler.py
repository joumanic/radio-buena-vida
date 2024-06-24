import os
import sys
from unittest.mock import patch, MagicMock
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
import unittest
from handler import logic_handler, process_image

# Mock Constants
MONTHLY_COLOR = (68, 239, 136)
FONT_PATH = "fonts/DejaVuSans-Bold.ttf"
FONT_SIZE = 24
IMAGE_DIR = '/data/'
OUTPUT_DIR = '/mnt/data/output'

class TestLogicHandler(unittest.TestCase):
    def logic_handler(self):
        event = {
            'trigger': True
        }
        context = {}
        response = logic_handler(event, context)
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('Images processed and uploaded successfully', response['body'])

class TestProcessImage(unittest.TestCase):
    @patch('PIL.Image.open')
    @patch('PIL.ImageFont.truetype')
    @patch('os.path.join', return_value='/mnt/data/radiobuenavida_logo.jpg')

    def test_process_image(self, mock_path_join, mock_truetype, mock_open):
        # Mock image object and its methods
        mock_img = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_img
        mock_img_copy = MagicMock()
        mock_img.copy.return_value = mock_img_copy
        mock_img_copy.resize.return_value = mock_img_copy
        mock_img_copy.filter.return_value = mock_img_copy

        # Mock for new image creation and drawing
        mock_img_new = MagicMock()
        Image.new = MagicMock(return_value=mock_img_new)
        ImageDraw.Draw = MagicMock()
        ImageDraw.Draw.return_value.textsize.return_value = (200, 50)
        
        # Mock logo processing
        mock_logo = MagicMock()
        mock_logo.convert.return_value = mock_logo
        mock_logo.getdata.return_value = [(255, 255, 255, 255)]
        mock_logo.size = (150, 150)
        mock_open.return_value.__enter__.return_value = mock_logo

        # Run the function
        process_image('data/raw/images/sample_image.jpg')

        # Assertions to verify the expected calls and operations
        mock_open.assert_called()
        mock_img.copy.assert_called_once()
        mock_img_copy.resize.assert_called_once()
        mock_img_copy.filter.assert_called_once()
        Image.new.assert_called_once()
        ImageDraw.Draw.assert_called_once()
        mock_truetype.assert_called_once_with(FONT_PATH, FONT_SIZE)
        mock_img_new.save.assert_called_once()
        process_image()

if __name__ == '__main__':
    unittest.main()
