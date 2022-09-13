import pytest
import time
from pathlib import Path
from os import getenv
from uuid import uuid4
from google.cloud import storage
import main
from deploy import deploy

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
        deploy_result = deploy(TEST_INPUT_BUCKET)
        return deploy_result

    @pytest.fixture(autouse=True, scope="class")
    def storage_client(self):
        # TODO: Use cached storage client once main has one
        sc = storage.Client()
        return sc

    @pytest.fixture()
    def patch_buckets(self, monkeypatch):
        monkeypatch.setenv('LIVE_INPUT_BUCKET', TEST_INPUT_BUCKET)
        monkeypatch.setattr(main, 'INPUT_BUCKET', TEST_INPUT_BUCKET)
        monkeypatch.setenv('LIVE_OUTPUT_BUCKET', TEST_OUTPUT_BUCKET)
        monkeypatch.setattr(main, 'OUTPUT_BUCKET', TEST_OUTPUT_BUCKET)

    @pytest.fixture()
    def input_bucket(self, storage_client, patch_buckets):
        tb = storage_client.get_bucket(TEST_INPUT_BUCKET)
        return tb

    @pytest.fixture()
    def output_bucket(self, storage_client, patch_buckets):
        ob = storage_client.get_bucket(main.OUTPUT_BUCKET)
        return ob

    @pytest.fixture(
        autouse=True, 
        params=main.MAX_DIMENSIONS.items()
    )
    def upload_test_image(self, request, deploy, storage_client, input_bucket):
        # Use random name per-test run in case cleanup fails.
        # Re-using the same image name will break future test
        # runs in the case that the test was halted before cleanup/delete.
        image_name = "{}.jpg".format(uuid4())
        blob = input_bucket.blob(image_name)
        blob.upload_from_filename(Path("./tests/test.jpg"))
        # Wait for Function call from upload to complete.
        time.sleep(90)

        yield image_name

        for size in main.MAX_DIMENSIONS:
            ds_blob = main.target_blob_path(image_name, size)
        blob.delete()

    def test_image_exists(self, request, upload_test_image):
        max_dimension = request.param[0]
        assert "image_exists"

    @pytest.mark.skip(reason="TODO")
    def test_exif_wiped(self, request, upload_test_image):
        max_dimension = request.param[0]
        assert "exif_wiped"

    @pytest.mark.skip(reason="TODO")
    def test_watermark_added(self, request, upload_test_image):
        max_dimension = request.param[0]
        assert "watermark_added"

    @pytest.mark.skip(reason="TODO")
    def test_expected_dimensions(self, request, upload_test_image):
        max_dimension = request.param[0]
        assert "expected_dimensions"
    
    @pytest.mark.skip(reason="TODO")
    def test_record_updated(self, request, upload_test_image):
        max_dimension = request.param[0]
        assert "record_updated"
