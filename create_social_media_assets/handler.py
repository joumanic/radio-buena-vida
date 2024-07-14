'''
Description:
Create social media assets for Radio Buena Vida
'''

import os 
from datetime import datetime
import pandas as pd
import logging
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT_PATH = "./data/fonts/din2014_demi.otf"
POST_SQUARE_SIZE= 1080
FONT_SHOW_SIZE_RATIO = 0.04
FONT_GENRE_SIZE_RATIO = 0.035

IMAGE_DIR = "./data/show_images"
OUTPUT_DIR = "./data/rbv_show_images"
RBV_LOGO_FOLDER = "./data/rbv_monthly_colors"
MONTHLY_COLORS_PATH = "data/monthly_colors/monthly_colors.xlsx"

# TODO handle different sizes of images so the branding is added with respective sizing

def logic_handler(event, context):
    """
    Handles the main logic when an event is triggered.

    Parameters:
    - event (dict): The event data containing the trigger status.
    - context: The context in which the function is executed.

    Returns:
    - dict: A response with the status code and body message.
    """
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
        imageFiles = [f for f in files if f.lower().endswith(('png', 'jpg', 'jpeg'))]

        # TODO 2. Loop through images
        for imageFile in imageFiles:
            imagePath = os.path.join(raw_images_path, imageFile)
        # TODO 4. Duplicate image
            try:
                img = process_image(image_path=imagePath)
                if img:
                    # Save show file
                    img.save(os.path.join(OUTPUT_DIR, imageFile), 'JPEG')
                else:
                    raise Exception
            except Exception as e:
                print(f"Error processing {imageFile}: {e}")

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
    """
    Processes an image by applying various transformations.

    Parameters:
    - image_path (str): The path to the image file.

    Returns:
    - Image or None: The processed image or None if processing failed.
    """
    rbvBrand = get_current_month_assets()
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
            maskedImage = circle_mask(img,rbvBrand['rgbColor'],0.04)
            
            maskedImagePosition  = (
                (imgSquare.width - maskedImage.width) // 2,
                (imgSquare.height - maskedImage.height) // 2
                ) # Calculate the position to paste the masked image (centre)
            imgSquare.paste(maskedImage, maskedImagePosition, maskedImage)

            # Make Show's Text
            # Calculate text size based on image size
            imageWidth, imageHeight = imgSquare.size
            draw = ImageDraw.Draw(imgSquare) # make draw instance in square canvas
            # Load the DIN 2014 font
            try:
                fontSize = int(imageHeight * FONT_SHOW_SIZE_RATIO)  # Calculate font size based on image height
                fontShow = ImageFont.truetype(FONT_PATH, fontSize)  # Adjust font path
            except IOError:
                logging.error("Could not load DIN 2014 font. Using default font for show name.")
                fontShow = ImageFont.load_default()

            showText = "David Barbarossa's Simple Food"
            showTextBbox = draw.textbbox((0, 0), showText, font=fontShow)
            showTextSize = (showTextBbox[2] - showTextBbox[0], showTextBbox[3] - showTextBbox[1])
            # Calculate dynamic position based on image size
            positionRatio=(0.05, 0.03)
            showTextX = int(imageWidth * positionRatio[0])
            showTextY = int(imageHeight * positionRatio[1])
            showTextPosition = (showTextX, showTextY)

            
            

            # Define the ratio
            marginRatio = 0.015  # 5% of the image dimensions
            # Define the rectangle roundness
            radius = 40
            # Calculate the rectangle margin based on the image dimensions
            rectangleMarginWidth = imageWidth * marginRatio
            rectangleMarginHeight = imageHeight * marginRatio

            roundedRectSize = (
                showTextPosition[0] - rectangleMarginWidth,
                showTextPosition[1] - rectangleMarginHeight,
                showTextPosition[0] + showTextSize[0] + rectangleMarginWidth,
                showTextPosition[1] + showTextSize[1] + rectangleMarginHeight
            ) 
            draw_rounded_rectangle(draw, roundedRectSize, radius, fill=rbvBrand["rgbColor"]) # Adjust color as needed
            draw.text(showTextPosition, showText, font=fontShow, fill="black") # draw show text in the square canvas

            # Make Genres' Text
            # TODO Make Genre Text bigger and postioning following template
             # Load the DIN 2014 font
            try:
                fontSize = int(imageHeight * FONT_GENRE_SIZE_RATIO)  # Calculate font size based on image height
                fontGenre = ImageFont.truetype(FONT_PATH, fontSize)  # Adjust font path
            except IOError:
                logging.error("Could not load DIN 2014 font. Using default font for shgenreow name.")
                fontGenre = ImageFont.load_default()

            genreText = "Disco | Boogie | Leftfield"
            genreTextBbox = draw.textbbox((0, 0), genreText, font=fontGenre)
            genreTextSize = (genreTextBbox[2] - genreTextBbox[0], genreTextBbox[3] - genreTextBbox[1])
            genreTextX = int(imageWidth * positionRatio[0])
            genreTextY = showTextPosition[1] + showTextSize[1] + int(imageHeight * 0.04)  # Adjust vertical position
            genreTextPosition = (genreTextX, genreTextY)

            genreRectSize = (
                genreTextPosition[0] - rectangleMarginWidth,
                genreTextPosition[1] - rectangleMarginHeight,
                genreTextPosition[0] + genreTextSize[0] + rectangleMarginWidth,
                genreTextPosition[1] + genreTextSize[1] + rectangleMarginHeight
            )
            draw_rounded_rectangle(draw, genreRectSize, radius, fill=rbvBrand["rgbColor"])
            draw.text(genreTextPosition, genreText, font=fontGenre, fill="black") # put Genre Text in the image


            # Add RBV logo into the show
            with Image.open(rbvBrand["logoFilePath"]) as rbvLogo:
                rbvLogo = rbvLogo.convert("RGBA")
            imgSquare = overlay_image(imgSquare, rbvLogo, 0.25, offsetPercentage=(0.05,0.075))

             # Add RBV website logo into the show
            with Image.open(rbvBrand["websiteLogoFilePath"]) as rbvWebsiteLogo:
                rbvWebsiteLogo = rbvWebsiteLogo.convert("RGBA")
            imgSquare = overlay_image(imgSquare, rbvWebsiteLogo, 0.25, offsetPercentage=(0.05,0.025))
            return imgSquare
        
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return None  # indicate failure if an exception was raised

def get_current_month_assets():
    """
    Fetches the assets for the current month.

    Returns:
    - dict: A dictionary containing the current month's assets including logo paths and colors.
    """
    currentMonthName = datetime.now().strftime("%B")
    rbvLogoFile = [file for file in os.listdir(RBV_LOGO_FOLDER) if currentMonthName.lower() in file.lower() and 'logo' in file.lower()][0]
    rbvLogoPath = os.path.join(RBV_LOGO_FOLDER, rbvLogoFile)
    rbvWebsiteLogoFile = [file for file in os.listdir(RBV_LOGO_FOLDER) if currentMonthName.lower() in file.lower() and 'website' in file.lower()][0]
    rbvWebsiteLogoPath = os.path.join(RBV_LOGO_FOLDER, rbvWebsiteLogoFile)
    monthlyColorsDf = pd.read_excel(MONTHLY_COLORS_PATH, header=0)
    hexColor = monthlyColorsDf["Color"].loc[monthlyColorsDf["Month"]==currentMonthName].values[0]

    rbvBrand = {
        "month": currentMonthName,
        "logoFilePath":rbvLogoPath,
        "websiteLogoFilePath": rbvWebsiteLogoPath,
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
    

def circle_mask(img: Image, borderColour: tuple, borderthickness_ratio: float = 0.04) -> Image:
    """
    Masks an image (`img`) to fit within a circular shape with a specified border.

    Parameters:
    - img (Image): Image file.
    - borderColour (tuple): Color tuple (R, G, B) for the circle border.
    - borderthickness_ratio (float, optional): Ratio of the border thickness to the diameter of the circle. Defaults to 0.02.

    Returns:
    - PIL.Image: Image with the original image masked within a circular shape with a border.
    """
    # Calculate the diameter of the circle
    diameter = min(img.size[0], img.size[1]) * 0.95
    radius = diameter // 2
    
    # Create a circular mask based on the image size
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    
    # Calculate bounding box for the circle mask
    bbox = (
        (img.size[0] - diameter) // 2,
        (img.size[1] - diameter) // 2,
        (img.size[0] + diameter) // 2,
        (img.size[1] + diameter) // 2
    )
    
    # Draw the outer circle for masking
    draw.ellipse(bbox, fill=255)
    
    # Create a new image for the masked result
    masked_image = Image.new("RGBA", img.size)
    masked_image.paste(img, (0, 0), mask)
    
    # Calculate the border thickness as a fraction of the diameter
    borderthickness = int(diameter * borderthickness_ratio)
    
    # If border thickness is specified, draw a border around the circle
    if borderthickness > 0:
        border_color = borderColour + (255,)  # Add alpha channel (fully opaque)
        
        # Create a new image for the border
        border_image = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw_border = ImageDraw.Draw(border_image)
        
        # Draw the outer border
        outer_bbox = (
            (bbox[0]) - borderthickness // 2,
            (bbox[1]) - borderthickness // 2,
            (bbox[2]) + borderthickness // 2,
            (bbox[3]) + borderthickness // 2
        )
        draw_border.ellipse(outer_bbox, outline=border_color, width=borderthickness)
        
       # Composite the masked image onto the border image
        border_image.paste(masked_image, (0, 0), mask=masked_image)
        return border_image
    else:
        return masked_image

def overlay_image(img: Image, overlayImage: Image,logoRatio=0.1,offsetPercentage=(0.05, 0.05)):
    """
    Overlays an image (e.g., logo) onto another image at a specified ratio.

    Parameters:
    - img (Image): The base image.
    - overlayImage (Image): The image to overlay.

    Returns:
    - Image: The image with the overlay applied.
    """

    # Calculate the new logo dimensions
    logoWidth = int(img.width * logoRatio)
    logoHeight = int(overlayImage.height * (logoWidth / overlayImage.width))

    # Resize the logo
    overlayImage = overlayImage.resize((logoWidth, logoHeight), Image.LANCZOS)

    # Calculate the proportional offset
    offset_x = int(img.width * offsetPercentage[0])
    offset_y = int(img.height * offsetPercentage[1])

    # Calculate position for the logo (bottom-right corner with offset)
    position = (img.width - logoWidth - offset_x, img.height - logoHeight - offset_y)

    # Overlay the logo on the image
    img.paste(overlayImage, position, overlayImage if overlayImage.mode == 'RGBA' else None)

    # Save the result
    return img

def draw_rounded_rectangle(draw, xy, radius, fill):
    """
    Draws a rounded rectangle on a given drawing context.

    Parameters:
    - draw: The drawing context.
    - xy (tuple): The bounding box of the rectangle (x0, y0, x1, y1).
    - radius (int): The radius of the corners.
    - fill: The fill color of the rectangle.
    """
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.pieslice([x0, y0, x0 + 2*radius, y0 + 2*radius], 180, 270, fill=fill)
    draw.pieslice([x1 - 2*radius, y0, x1, y0 + 2*radius], 270, 360, fill=fill)
    draw.pieslice([x0, y1 - 2*radius, x0 + 2*radius, y1], 90, 180, fill=fill)
    draw.pieslice([x1 - 2*radius, y1 - 2*radius, x1, y1], 0, 90, fill=fill)

def hex_to_rgb(hex_color):
    """
    Converts a hex color string to an RGB tuple.

    Parameters:
    - hex_color (str): The hex color string.

    Returns:
    - tuple: The RGB color as a tuple.
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

if __name__ == '__main__':
    logic_handler(event = {'trigger': True}, context =  None)