import functions_framework
import tempfile
from os import getenv
import PIL
from google.cloud import storage

OUTPUT_BUCKET = getenv('OUTPUT_BUCKET')
# TODO: Research suitable dimensions and names based on publishing and site needs.
MAX_DIMENSIONS = {"max": 1200,
                  "feed": 512,
                  "tile": 288,
                  "thumb": 128}
MATERIAL_SOUL_WATERMARK = "TODO"

# Initialize cache for clients, requests sessions, DB-connections, etc.
# Global-scope code is executed on cold starts only.
firestore_client = "TODO"
# Use lazy initialization if there is any chance a reference won't be used.
storage_client = None

@functions_framework.cloud_event
def process_public_images(cloud_event):
    """Process images for public consumption.
    - Create 
    """
    data = cloud_event.data
    local_image = download_image(data["bucket"], data["name"])
    public_images = create_smaller_copies(local_image)
    upload_to_output(public_images)

def blob_name(image_name, description):
    """Enforce a standard naming convention for downstream buckets.

    Args:
        image_name (str): Image name.
        description (str): Size description.

    Returns:
        (str): New image name.
    """
    return f"{image_name}-{description}"

def download_image(bucket, name, local_dir):
    """Download uploaded image into local directory.
    
    Args:
        bucket ()
    """

def storage_client():
    """Return storage client and initialize if needed."""
    global storage_client
    if not storage_client:
        storage_client = storage.Client()
    return storage_client

def create_smaller_copies(image_path):
    """Create smaller copies of images according to MAX_DIMENSIONS.

    Args:
        image_path (path-like): A local path to an image.

    Returns:
        (list of path-like): List of smaller-copy paths.
    """
    pass

def upload_to_output(public_images):
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

def add_eventid_to_db(image, event_id):
    """Add a reference to the eventid as confirmation we processed this image.
    """
    pass
