import pytest
import subprocess
from pathlib import Path
from os import getenv
from uuid import uuid4
from google.cloud import storage
import main

PROJECT = getenv('GCP_PROJECT')
TEST_BUCKET = getenv('TEST_BUCKET')

class TestUnit:
    pass

class TestIntegration:
    pass

class TestSystem:
    """Tests that run against live system.
    """
    @pytest.fixture
    def deploy():
        subprocess.run(['./deploy.sh', TEST_BUCKET])

    @pytest.fixture
    def storage_client():
        yield storage.Client()

    @pytest.fixture
    def test_bucket(storage_client):
        yield storage_client.get_bucket(TEST_BUCKET)

    @pytest.fixture
    def upload_test_image(test_bucket):
        # Use random name per-test run in case cleanup fails.
        # Re-using the same image name will break future test
        # runs in the case that the test was halted before cleanup/delete.
        image_name = "{}.jpg".format(uuid4())
        blob = test_bucket.blob(image_name)
        # TODO: Figure out high-resolution test file suitable for making assertions against.
        #       Maybe something like the emergency-broadcast image from TV?
        blob.upload_from_filename(Path("./test.jpg"))
        yield image_name

    def test_pub_proc_image(upload_test_image):
        """Test that each intended image copy is to-size and 
        that each resulting file is cleaned and watermarked.
        """
        for dimension in main.MAX_DIMENSIONS:
            # TODO: assert processed_image exists at expected bucket path
            # TODO: assert file has no sensitive exif data
            # TODO: assert watermark has been added???
            #         - how? assert expected-watermarked pixel has been darkened?
            # TODO: assert max(width, height) <= main.MAX_DIMENSIONS[dimension]
            # TODO: assert main.already_processed(image) returns True
            pass
