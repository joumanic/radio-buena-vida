import os
import sys
from unittest.mock import patch, MagicMock
from PIL import Image
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
import unittest
from handler import logic_handler, process_image, zoom_image, blur_image, hex_to_rgb

class TestImageProcessingFunctions(unittest.TestCase):

    @patch('os.listdir')
    @patch('os.getenv')
    @patch('handler.process_image')  # Replace 'your_module_name' with the actual module name where the process_image function is defined
    def test_logic_handler_triggered(self, mock_process_image, mock_getenv, mock_listdir):
        """
        Tests the main logic handler when the trigger event is True.
        """
        # Mock environment variables and directory listing
        mock_getenv.return_value = 'test/raw_images'
        mock_listdir.return_value = ['image1.jpg', 'image2.png', 'document.pdf']
        
        with patch('builtins.print'):
            mock_process_image.side_effect = [Image.new('RGB', (100, 100)), None]
                
            event = {'trigger': True}
            context = None
            response = logic_handler(event, context)
                
            # Check that process_image is called twice (for two images)
            self.assertEqual(mock_process_image.call_count, 2)
                
            # Verify the response
            self.assertEqual(response['statusCode'], 200)
            self.assertEqual(response['body'], 'Images processed and uploaded successfully')

    @patch('os.listdir')
    @patch('os.getenv')
    def test_logic_handler_directory_not_found(self, mock_getenv, mock_listdir):
        """
        Tests the main logic handler when the raw_images directory is not found.
        """
        # Mock environment variable and simulate FileNotFoundError
        mock_getenv.return_value = 'invalid/path'
        mock_listdir.side_effect = FileNotFoundError
        
        event = {'trigger': True}
        context = None
        response = logic_handler(event, context)
        
        # Verify the response
        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(response['body'], 'raw_images directory not found')

    @patch('handler.get_current_month_assets')  # Replace 'your_module_name' with the actual module name where the get_current_month_assets function is defined
    class TestImageProcessingFunctions(unittest.TestCase):

    @patch('your_module_name.get_current_month_assets')  # Replace 'your_module_name' with the actual module name where the get_current_month_assets function is defined
    def test_process_image_success(self, mock_get_assets):
        """
        Tests the process_image function with a valid image path.
        """
        mock_get_assets.return_value = {
            "month": "January",
            "logoFilePath": "path/to/logo.png",
            "circleFilePath": "path/to/circle.png",
            "hexColor": "#FFFFFF",
            "rgbColor": (255, 255, 255)
        }
        
        # Create a sample image to test
        test_image_path = 'test_image.jpg'
        with Image.new('RGB', (100, 100)) as img:
            img.save(test_image_path)
        
        # Ensure the image file is correctly created
        self.assertTrue(os.path.exists(test_image_path))
        
        # Test the process_image function
        result_img = process_image(test_image_path)
        
        # Check if the result is not None
        logging.info(f"Result image: {result_img}")
        self.assertIsNotNone(result_img)
        self.assertIsInstance(result_img, Image.Image)
        
        # Clean up
        if os.path.exists(test_image_path):
            os.remove(test_image_path)

            
    def test_zoom_image(self):
        """
        Tests the zoom_image function.
        """
        with Image.new('RGB', (100, 100)) as img:
            zoomed_img = zoom_image(img)
            
            # Check if the zoomed image has the correct size
            expected_size = (150, 150)  # 1.5 times the original size
            self.assertEqual(zoomed_img.size, expected_size)
    
    def test_blur_image(self):
        """
        Tests the blur_image function.
        """
        with Image.new('RGB', (100, 100)) as img:
            blurred_img = blur_image(img)
            
            # Check if the blurred image is an instance of Image
            self.assertIsInstance(blurred_img, Image.Image)
    
    def test_hex_to_rgb(self):
        """
        Tests the hex_to_rgb function.
        """
        hex_color = "#FFAABB"
        rgb_color = hex_to_rgb(hex_color)
        
        # Check if the RGB conversion is correct
        self.assertEqual(rgb_color, (255, 170, 187))

if __name__ == '__main__':
    unittest.main()