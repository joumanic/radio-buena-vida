import os
import sys
from unittest.mock import patch, MagicMock
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
import unittest
from handler import logic_handler, process_image, get_current_month_assets, zoom_image, blur_image, circle_mask, overlay_image, draw_rounded_rectangle, hex_to_rgb

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

    def test_get_current_month_assets(self):
        # Test the function that retrieves current month assets
        result = get_current_month_assets()

        self.assertIsInstance(result, dict)
        self.assertIn("month", result)
        self.assertIn("month", result)
        self.assertIn("logoFilePath", result)
        self.assertIn("circleFilePath", result)
        self.assertIn("hexColor", result)
        self.assertIn("rgbColor", result)
        self.assertIsInstance(result["rgbColor"], tuple)
        self.assertEqual(len(result["hexColor"]), 7)  # Assuming hex color format like #RRGGBB
        self.assertEqual(len(result["rgbColor"]), 3)
    
    def test_zoom_image(self):
        # Test zoom image function
        img = Image.new('RGB', (100,100))
        result = zoom_image(img, zoomFactor=2.0)
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, (200,200))

    def text_blur_image(self):
        img = Image.new('RGB', (100,100))
        result = blur_image(img, blurFactor = 10)

        self.assertIsInstance(result, Image.Image)

    def test_circle_mask(self):
        # Test the circle mask function
        img = Image.new('RGB', (100,100))
        borderColour = (250,0,0)
        result = circle_mask(img, borderColour)

        self.assertIsInstance(result, borderColour)
    
    def text_overlay_image(self):
        # Test the overlay_image function
        img = Image.new('RGB', (200, 200))
        overlay = Image.new('RGBA', (50, 50), (255, 255, 255, 128))
        result = overlay_image(img, overlay)
        
        self.assertIsInstance(result, Image.Image)
    
    def test_draw_rounded_rectangle(self):
        # Test the draw_rounded_rectangle function
        img = Image.new('RGB', (200, 200))
        draw = ImageDraw.Draw(img)
        xy = (10, 10, 100, 100)
        radius = 10
        fill = (255, 0, 0)
        
        draw_rounded_rectangle(draw, xy, radius, fill)
        # Add assertions if necessary to verify the drawing

    def test_hex_to_rgb(self):
        # Test the hex_to_rgb function
        hex_color = "#FF0000"
        result = hex_to_rgb(hex_color)
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(result, (255, 0, 0))


if __name__ == '__main__':
    unittest.main()
