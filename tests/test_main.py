import pytest
import time
from pathlib import Path
from os import getenv
from uuid import uuid4
from google.cloud import storage
import main
import deploy

PROJECT = getenv('GCP_PROJECT')
TEST_INPUT_BUCKET = getenv('TEST_INPUT_BUCKET')
TEST_OUTPUT_BUCKET = getenv('TEST_OUTPUT_BUCKET')

class TestUnit:
    pass

class TestIntegration:
    pass

class TestSystem:
    """Tests that run against live system.
    """
    @pytest.fixture(autouse=True, scope="class")
    def deploy(self):
        deploy_result = deploy.deploy(TEST_INPUT_BUCKET, 
            output_bucket=TEST_OUTPUT_BUCKET)
        return deploy_result

    @pytest.fixture(autouse=True, scope="class")
    def storage_client(self):
        # TODO: Use cached storage client once main has one
        sc = storage.Client()
        return sc

    @pytest.fixture(scope="class")
    def input_bucket(self, storage_client):
        tb = storage_client.get_bucket(TEST_INPUT_BUCKET)
        return tb

    @pytest.fixture(scope="class")
    def output_bucket(self, storage_client):
        ob = storage_client.get_bucket(TEST_OUTPUT_BUCKET)
        return ob

    @pytest.fixture(scope="class")
    def upload_test_image(self, input_bucket):
        # Use random name per-test run in case cleanup fails.
        # Re-using the same image name will break future test
        # runs in the case that the test was halted before cleanup/delete.
        image_name = "{}.jpg".format(uuid4())
        blob = input_bucket.blob(image_name)
        blob.upload_from_filename(Path("./tests/test.jpg"))
        # Wait for Function call from upload to complete.
        time.sleep(45)

        yield image_name

        for size in main.MAX_DIMENSIONS:
            ds_blob = main.target_blob_path(image_name, size)
        blob.delete()

    @pytest.fixture(params=main.MAX_DIMENSIONS.items())
    def fanout_by_dimensions(self, upload_test_image, request):
        return upload_test_image, request.param

    def test_image_exists(self, input_bucket, fanout_by_dimensions):
        image = fanout_by_dimensions[0]
        dimension_name = fanout_by_dimensions[1][0]
        max_dimension = fanout_by_dimensions[1][1]
        assert input_bucket.blob(image).exists()

    @pytest.mark.skip(reason="TODO")
    def test_exif_wiped(self):
        assert "exif_wiped"

    @pytest.mark.skip(reason="TODO")
    def test_watermark_added(self):
        assert "watermark_added"

    @pytest.mark.skip(reason="TODO")
    def test_expected_dimensions(self):
        assert "expected_dimensions"
    
    @pytest.mark.skip(reason="TODO")
    def test_record_updated(self):
        assert "record_updated"
