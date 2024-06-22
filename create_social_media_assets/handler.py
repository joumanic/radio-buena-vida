'''
Description:
Create social media assets for Radio Buena Vida
'''

import os 
from PIL import Image, ImageDraw, ImageFilter, ImageFont

MONTHLY_COLOR = (68, 239, 136)
FONT_PATH = "/create_social_media_assets/data/fonts/dejavu-sans/DejaVuSans-Bold.ttf"
FONT_SIZE = 24
IMAGE_DIR = "/create_social_media_assets/data/raw_images"
OUTPUT_DIR = "/create_social_media_assets/data/rbv_images"
RBV_LOGO_PATH = "/create_social_media_assets/data/radiobuenavida_logo.jpg"
WORKING_DIRECTORY = os.getcwd()
def lambda_handler(event, context):
    if event['trigger'] == True:
        # TODO 1. Look for folder in DROPBOX to process images
            # REPLACEMENT: Grab an example image
        raw_images_path = os.getenv('RAW_IMAGES_PATH')
        # List all files in the raw_images directory
        try:
            files = os.listdir(raw_images_path)
        except FileNotFoundError:
            return {
                'statusCode': 500,
                'body': 'raw_images directory not found'
            }
        
        # Filter for image files (assuming common image extensions)
        image_files = [f for f in files if f.lower().endswith(('png', 'jpg', 'jpeg'))]

        # TODO 2. Loop through images
        for image_file in image_files:
            image_path = os.path.join(raw_images_path, image_file)
        # TODO 4. Duplicate image
            try:
                process_image(image_path=image_path)
            except Exception as e:
                print(f"Error processing {image_file}: {e}")

        return {
            "statusCode": 200,
            "body": 'Images processed and uploaded successfully'
        }
    else:
        return {
            "statusCode": 300,
            "body": 'Not Triggered'
        }

def process_image(image_path):
    with Image.open(image_path) as img:
        try:
            # Duplicate image
            img_copy = img.copy()

            # Create Zoomed + Blurred Image
            zoom_factor = 1.5
            img_zoomed = img_copy.resize(
                (int(img_copy.width * zoom_factor), int(img_copy.height * zoom_factor)),
                resample=Image.LANCZOS
            )
            img_blurred = img_zoomed.filter(ImageFilter.GaussianBlur(15))

            # Determine the size for the square image
            size = min(img_blurred.width, img_blurred.height)
            
            # Create a square canvas
            img_square = Image.new("RGB", (size, size))
            
            # Paste the zoomed and blurred image onto the square canvas
            offset = ((size - img_blurred.width) // 2, (size - img_blurred.height) // 2)
            img_square.paste(img_blurred, offset)

            # TODO Make circled image and paste it on top of blurred image

            # Draw Show Text
            draw = ImageDraw.Draw(img_square)
            
            # Using a default font (adjust the size as necessary)
            font = ImageFont.load_default()  

            # TODO Make Genre Text bigger and postioning following template 
            show_text = "David Barbarossa's Simple Food"
            show_text_bbox = draw.textbbox((0, 0), show_text, font=font)
            show_text_size = (show_text_bbox[2] - show_text_bbox[0], show_text_bbox[3] - show_text_bbox[1])
            show_text_position = (10, 10)

            # Draw rounded rectangle for Show Text
            rectangle_margin = 10
            rounded_rect_size = (
                show_text_position[0] - rectangle_margin,
                show_text_position[1] - rectangle_margin,
                show_text_position[0] + show_text_size[0] + rectangle_margin,
                show_text_position[1] + show_text_size[1] + rectangle_margin
            )
            draw.rectangle(rounded_rect_size, outline=None, fill=MONTHLY_COLOR, width=0)
            
            # Put Show Text in the image
            draw.text(show_text_position, show_text, font=font, fill="black")

            # TODO Make Genre Text bigger and postioning following template 
            # Draw Genre Text
            genre_text = "Disco | Boogie | Leftfield"
            genre_text_bbox = draw.textbbox((0, 0), genre_text, font=font)
            genre_text_size = (genre_text_bbox[2] - genre_text_bbox[0], genre_text_bbox[3] - genre_text_bbox[1])
            genre_text_position = (10, show_text_position[1] + show_text_size[1] + 20)

            
            # Draw rounded rectangle for Genre Text
            genre_rect_size = (
                genre_text_position[0] - rectangle_margin,
                genre_text_position[1] - rectangle_margin,
                genre_text_position[0] + genre_text_size[0] + rectangle_margin,
                genre_text_position[1] + genre_text_size[1] + rectangle_margin
            )
            draw.rectangle(genre_rect_size, outline=None, fill=MONTHLY_COLOR, width=0)

            # Put Genre Text in the image
            draw.text(genre_text_position, genre_text, font=font, fill="black")

            # Load and replace white color to monthly color for Radio Buena Vida Logo
            logo_path = WORKING_DIRECTORY + RBV_LOGO_PATH  # Assuming logo path
            with Image.open(logo_path) as logo:
                logo = logo.convert("RGBA")
                data = logo.getdata()
                new_data = [
                    (MONTHLY_COLOR[0], MONTHLY_COLOR[1], MONTHLY_COLOR[2], item[3]) if item[:3] == (255, 255, 255) else item
                    for item in data
                ]
                logo.putdata(new_data)

            # TODO Resize and place the logo accordingly following template
            # Resize and place the logo
            logo_size = (150, 150)  # Adjust size as necessary
            logo.thumbnail(logo_size)
            logo_position = (img_square.width - logo.width - 20, img_square.height - logo.height - 20)
            img_square.paste(logo, logo_position, logo)

            return True
        
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return False  # Indicate failure if an exception was raised

if __name__ == '__main__':
    lambda_handler(event = {'trigger': True}, context =  None)