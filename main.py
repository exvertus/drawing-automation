from statistics import mode
import functions_framework
from os import getenv
from pathlib import Path
from PIL import Image
from google.cloud import storage

OUTPUT_BUCKET = getenv('OUTPUT_BUCKET')
ARTIFACTS_DIR = getenv('IMAGE_ARTIFACTS_DIR')
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
gcp_storage_client = None

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
    return f"{description}/{image_name}"

def storage_client():
    """Return storage client and initialize if needed."""
    global gcp_storage_client
    if not gcp_storage_client:
        gcp_storage_client = storage.Client()
    return gcp_storage_client

def download_image(bucket, name):
    """Download uploaded image into current working directory.
    
    Args:
        bucket (str): Storage Bucket.
        name (str): Image name:

    Returns:
        (path-like): local path of image
    """
    client = storage_client()
    src_bucket = storage.Bucket(client, name=bucket)
    blob = storage.Blob(name, src_bucket)
    local_file = Path('.') / name
    with local_file.open(mode='w') as lf:
        client.download_blob_to_file(blob, lf)
    return local_file

def create_smaller_copies(image_path):
    """Create smaller copies of image according to MAX_DIMENSIONS.

    Args:
        image_path (path-like): A local path to an image.

    Returns:
        (list of path-like): List of smaller-copy paths.
    """
    origin_image = Image.open(image_path)
    print('break')
    for key, val in MAX_DIMENSIONS.items():
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
