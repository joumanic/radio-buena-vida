import requests
import logging
import json
import os
from requests.exceptions import RequestException, HTTPError, Timeout, ConnectionError



# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_images():
    url = "https://api.dropboxapi.com/2/files/list_folder"
    headers = {
    "Authorization": "Bearer " + os.getenv('DROPBOX_TOKEN'),
    "Content-Type": "application/json"
    }

    data = {
        "path": ""
    }

    try:
        logger.info("Sending request to Dropbox API")
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status() # Raises an HTTPError for bad responses
        logger.info("Request sucessful.")
        return response.json()
    except HTTPError as httpErr:
        logger.error(f"HTTP error ocurred: {httpErr}")
    except Timeout as timeoutErr:
        logger.error(f"Request timed out: {timeoutErr}")
    except ConnectionError as connErr:
        logger.error(f"Connection error occured: {connErr}")
    except RequestException as reqErr:
        logger.error(f"An error ocurred: {reqErr}")
    except Exception as err:
        logger.error(f"An unexpected error ocurred: {err}")
    
    return None