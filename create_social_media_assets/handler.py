'''
Description:
Create social media assets for Radio Buena Vida
'''

import os 
from datetime import datetime
import pandas as pd
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT_PATH = "./data/fonts/dejavu-sans/DejaVuSans-Bold.ttf"
FONT_SHOW_SIZE = 32
FONT_GENRE_SIZE = 18
POST_SQUARE_SIZE= 1080
IMAGE_DIR = "./data/show_images"
OUTPUT_DIR = "./data/rbv_show_images"
RBV_LOGO_FOLDER = "./data/rbv_monthly_colors"
MONTHLY_COLORS_PATH = "data/monthly_colors/monthly_colors.xlsx"

# TODO handle different sizes of images so they fit into a square canvas

def logic_handler(event, context):
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
                img = process_image(image_path=image_path)
                if img:
                    # Save show file
                    img.save(os.path.join(OUTPUT_DIR, 'output_image.jpg'), 'JPEG')
                else:
                    raise Exception
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
    rbvBrand = getCurrentMonthAssets()
    with Image.open(image_path) as img:
        try:
            imgCopy = img.copy()

            # Blur and Zoom image
            imgBlurZoom = zoom_image(blur_image(imgCopy)) 
            

            # Create square canvas for instagram post
            size = min(imgBlurZoom.width, imgBlurZoom.height) # determine the size for the square image
            imgSquare = Image.new("RGB", (size,size)) # create a square canvas
            offset = ((size - imgBlurZoom.width) // 2, (size - imgBlurZoom.height) // 2)
            imgSquare.paste(imgBlurZoom, offset)  # Paste the zoomed and blurred image onto the square canvas

            # Make circled image and paste it on top of blurred image
            maskedImage = circle_mask(img,rbvBrand['rgbColor'],80)
            #maskedImage = resize_image(maskedImage)
            
            maskedImagePosition  = (
                (imgSquare.width - maskedImage.width) // 2,
                (imgSquare.height - maskedImage.height) // 2
                ) # Calculate the position to paste the masked image (centre)
            imgSquare.paste(maskedImage, maskedImagePosition, maskedImage)

            # Make Show's Text
            # TODO Make Show Text bigger and postioning following template 
            draw = ImageDraw.Draw(imgSquare) # make draw instance in square canvas
            font = ImageFont.load_default(size=FONT_SHOW_SIZE) 
            showText = "David Barbarossa's Simple Food"
            showTextBbox = draw.textbbox((0, 0), showText, font=font)
            showTextSize = (showTextBbox[2] - showTextBbox[0], showTextBbox[3] - showTextBbox[1])
            showTextPosition = (10, 10)

            
            rectangleMargin = 10
            roundedRectSize = (
                showTextPosition[0] - rectangleMargin,
                showTextPosition[1] - rectangleMargin,
                showTextPosition[0] + showTextSize[0] + rectangleMargin,
                showTextPosition[1] + showTextSize[1] + rectangleMargin
            ) 
            draw.rectangle(roundedRectSize, outline=None, fill=rbvBrand["rgbColor"], width=0) # draw rounded rectangle for Show's Text
            draw.text(showTextPosition, showText, font=font, fill="black") # draw show text in the square canvas

            # Make Genres' Text
            # TODO Make Genre Text bigger and postioning following template 
            font = ImageFont.load_default(size=FONT_GENRE_SIZE)  
            genreText = "Disco | Boogie | Leftfield"
            genreTextBbox = draw.textbbox((0, 0), genreText, font=font)
            genreTextSize = (genreTextBbox[2] - genreTextBbox[0], genreTextBbox[3] - genreTextBbox[1])
            genreTextPosition = (10, showTextPosition[1] + showTextSize[1] + 20)

            genre_rect_size = (
                genreTextPosition[0] - rectangleMargin,
                genreTextPosition[1] - rectangleMargin,
                genreTextPosition[0] + genreTextSize[0] + rectangleMargin,
                genreTextPosition[1] + genreTextSize[1] + rectangleMargin
            )
            draw.rectangle(genre_rect_size, outline=None, fill=rbvBrand['rgbColor'], width=0) # draw rounded rectangle for Genre Text
            draw.text(genreTextPosition, genreText, font=font, fill="black") # put Genre Text in the image


            # Add RBV logo into the show
            # TODO Resize and place the logo accordingly following template
            with Image.open(rbvBrand["logoFilePath"]) as rbvLogo:
                rbvLogo = rbvLogo.convert("RGBA")

            logoSize = (250, 180)  # adjust size as necessary
            rbvLogo.thumbnail(logoSize)
            logo_position = (imgSquare.width - rbvLogo.width - 20, imgSquare.height - rbvLogo.height - 20) # adjust position of the logo 
            imgSquare.paste(rbvLogo, logo_position, rbvLogo)

            return imgSquare
        
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return None  # indicate failure if an exception was raised

def getCurrentMonthAssets():
    currentMonthName = datetime.now().strftime("%B")
    rbvLogoFile = [file for file in os.listdir(RBV_LOGO_FOLDER) if currentMonthName.lower() in file.lower() and 'logo' in file.lower()][0]
    rbvCircleFile = [file for file in os.listdir(RBV_LOGO_FOLDER) if currentMonthName.lower() in file.lower() and 'circle' in file.lower()][0]
    rbvLogoPath = os.path.join(RBV_LOGO_FOLDER, rbvLogoFile)
    rbvCircleLogoPath = os.path.join(RBV_LOGO_FOLDER, rbvCircleFile)
    monthlyColorsDf = pd.read_excel(MONTHLY_COLORS_PATH, header=0)
    hexColor = monthlyColorsDf["Color"].loc[monthlyColorsDf["Month"]==currentMonthName].values[0]

    rbvBrand = {
        "month": currentMonthName,
        "logoFilePath":rbvLogoPath,
        "circleFilePath": rbvCircleLogoPath,
        "hexColor": hexColor,
        "rgbColor": hex_to_rgb(hexColor)
    }

    return rbvBrand

def zoom_image(img: Image, zoomFactor: float =1.5) -> Image:
    """
    Zooms into an image by a specified zoom factor.

    Parameters:
    img (Image): The input image to be zoomed.
    zoom_factor (float, optional): The factor by which to zoom into the image. Default is 1.5.

    Returns:
    Image: The zoomed image.
    """
    imgZoomed = img.resize(
        (int(img.width * zoomFactor), int(img.height * zoomFactor)),
        resample=Image.LANCZOS
    )
    return imgZoomed

def blur_image(img: Image, blurFactor: float = 15) -> Image:

    """
    Applies a Gaussian blur to an image.

    Parameters:
    img (Image): The input image to be blurred.

    Returns:
    Image: The blurred image.
    """
    imgBlurred = img.filter(ImageFilter.GaussianBlur(blurFactor))
    return imgBlurred
    

    """
    Masks an image (`img`) to fit within the filled area of a outline (`maskImg`).

    Parameters:
    - img (Image): Image file.
    - maskImg (PIL.Image): Image object representing the outline.

    Returns:
    - PIL.Image: Image with the original image masked within the filled area of `circleImg`.
    """
    # Resize the original image to fit within the circle image
    dancingImageResized = img.resize(maskImg.size, Image.LANCZOS)

    # Create a mask from the circle image's alpha channel
    circleMask = maskImg.split()[3]

    # Ensure the mask has the correct size and transparency
    mask = Image.new("L", maskImg.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, maskImg.width, maskImg.height), fill=255)

    # Create a new image with an alpha layer (RGBA)
    result = Image.new("RGBA", maskImg.size)
    result.paste(dancingImageResized, (0, 0), mask)

    # Composite the circle image (with borders) on top of the result
    result_with_border = Image.alpha_composite(result, maskImg)

    return result_with_border

def circle_mask(img: Image, borderColour: tuple,borderthickness: int = 0) -> Image:
    """
    Masks an image (`img`) to fit within a circular shape with a specified border.

    Parameters:
    - img (Image): Image file.
    - borderColour (tuple): Color tuple (R, G, B) for the circle border.
    - borderThickness (int, optional): Thickness of the border in pixels. Defaults to 0.

    Returns:
    - PIL.Image: Image with the original image masked within a circular shape with a border.
    """
    # Calculate the diameter of the circle
    diameter = min(img.size[0], img.size[1])
    radius = diameter // 2

    # Calculate the bounding box for the circle
    bbox = (
        (img.size[0] - diameter) // 2,
        (img.size[1] - diameter) // 2,
        (img.size[0] + diameter) // 2,
        (img.size[1] + diameter) // 2)
    
    # Create a circular mask based on the image size
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse(bbox, fill=255)

    # Apply the circular mask to the original image
    masked_image = Image.new("RGBA", img.size)
    masked_image.paste(img, (0, 0), mask)

    # If borderThickness is specified, draw a border around the circle
    if borderthickness > 0:
        border_color = borderColour + (255,)  # Add alpha channel (fully opaque)
        draw = ImageDraw.Draw(masked_image)
        draw.ellipse(bbox, outline=border_color, width=borderthickness)

    return masked_image


def resize_image(img:Image, resize_factor: float = 1) -> Image:
    # Determine the new size based on resize factor
    newSize = (int(img.width * resize_factor), int(img.height * resize_factor))

    # Resize the image to the new size
    imgResized = img.resize(newSize, Image.LANCZOS)

    return imgResized

def hex_to_rgb(hex_color):
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

if __name__ == '__main__':
    logic_handler(event = {'trigger': True}, context =  None)