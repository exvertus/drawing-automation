"""
GCP Function deployed as a Cloud Storage event for creating
copies of images suitable for public consumption:
    - obfuscates exif data
    - adds custom watermark
    - scales down to a max resolution
      - thumbnail generation
"""

import functions_framework
from os import getenv

BUCKET_NAME_JOINER = "-"
INPUT_BUCKET = getenv('LIVE_INPUT_BUCKET')
OUTPUT_BUCKET = getenv('LIVE_OUTPUT_BUCKET')
# TODO: Research suitable dimensions and names based on publishing and site needs.
MAX_DIMENSIONS = {"large": 1024,
                  "thumbnail": 256}
MATERIAL_SOUL_WATERMARK = "TODO"

# Initialize cache for clients, requests sessions, DB-connections, etc.
# Global-scope code is executed on cold starts only.
# Use lazy initialization if there is any chance a reference won't be used.
storage_client = None

@functions_framework.cloud_event
def process_public_images(cloud_event):
    event_id = cloud_event["id"]
    image = cloud_event.data["name"]
    if already_processed(image):
        return image
    cleaned_image = add_watermark(obfuscate_exif(image), MATERIAL_SOUL_WATERMARK)
    public_images = shrink_images(cleaned_image, MAX_DIMENSIONS)
    add_eventid_to_db(image, event_id)
    return image

def target_blob_path(image_name, description=""):
    pass

def already_processed(image):
    """True if image already has an event-id in the database.
    """
    pass

def obfuscate_exif(image):
    """Return image with sensitive exif data removed.
    """
    pass

def add_watermark(image, watermark):
    """Return image with a custom watermark added.
    """
    pass

def shrink_images(image, max_dict=MAX_DIMENSIONS):
    """Return images scaled down according to max_dict.
    """
    pass

def add_eventid_to_db(image, event_id):
    """Add a reference to the eventid as confirmation we processed this image.
    """
    pass
