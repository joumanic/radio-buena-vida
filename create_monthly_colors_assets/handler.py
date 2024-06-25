'''
Description:

'''

import os 
from PIL import Image
import pandas as pd

# Temporary paths while we integrate in Dropbox
RBV_BRAND_FOLDER = "data/rbv_brand"
MONTHLY_COLORS = "data/monthly_colors/monthly_colors.xlsx"
OUTPUT_FOLDER = "data/rbv_monthly_colors"
# Dictionary to map month names to month numbers
MONTH_NAME_TO_NUMBER = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12
}


def logic_handler():
    # TODO look for folder with blank assets
    # Load and replace white color to monthly color for Radio Buena Vida Logo
    monthlyColorsDf = pd.read_excel(MONTHLY_COLORS, header=0)
    for index, row in monthlyColorsDf.iterrows():
        monthName = row['Month']
        monthNumber = MONTH_NAME_TO_NUMBER.get(monthName.replace(" ",""))
        hexColor = row['Color']
        monthlyColor = hex_to_rgb(hexColor)

        brandFiles = [file for file in os.listdir(RBV_BRAND_FOLDER) if '.DS_Store' not in file]
        
        for fileName in brandFiles:
            filePath = os.path.join(RBV_BRAND_FOLDER, fileName)
            fileBaseName, _ = os.path.splitext(fileName)
            with Image.open(filePath) as logo:
                logo = logo.convert("RGBA")
                data = logo.getdata()
                new_data = [
                    (monthlyColor[0], monthlyColor[1], monthlyColor[2], item[3]) if item[:3] == (255, 255, 255) else item
                    for item in data
                ]
                logo.putdata(new_data)
                
                # Save the new logo with the month number and month name in the filename
                output_path = os.path.join(OUTPUT_FOLDER, f"{monthNumber}_{monthName}_{fileBaseName}.png")
                logo.save(output_path)

    # TODO process assets to Monthly Colors file specifications
    # TODO upload assets to Dropbox
    # TODO if somethin in the Monthly Colors file changes then change colors 

    return 'RBV asset images processed and uploaded succesfully'


def hex_to_rgb(hex_color):
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
