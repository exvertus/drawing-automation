import datetime
import pytest
import shlex
import subprocess
import requests
import time
from pathlib import Path
from os import getenv
from uuid import uuid4
from google.cloud import storage

import deploy
import main

PROJECT = getenv('GCP_PROJECT')
TEST_INPUT_BUCKET = getenv('TEST_INPUT_BUCKET')
TEST_OUTPUT_BUCKET = getenv('TEST_OUTPUT_BUCKET')
LOCAL_PORT = 8099
LOCAL_URL = f"http://localhost:{LOCAL_PORT}/"

class TestUnit:
    pass

class TestIntegrationFuncFW:
    """'Narrow' itegration tests 
    running against functions-framework dependency.
    """
    @pytest.fixture(scope='class', autouse=True)
    def init_functions_framework(self):
        ff_cmd = "functions-framework --target process_public_images "\
            f"--signature-type event --port {LOCAL_PORT}"
        args = shlex.split(ff_cmd)
        ff_process = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=Path(__file__).parents[1])

        yield ff_process

        ff_process.terminate()
    
    @pytest.fixture(scope='class')
    def mounted_session(self):
        retry_policy = requests.packages.urllib3.util.retry.Retry(
            total=6, backoff_factor=1)
        retry_adapter = requests.adapters.HTTPAdapter(
            max_retries=retry_policy)
        session = requests.Session()
        session.mount(LOCAL_URL, retry_adapter)
        return session

    @pytest.fixture()
    def trigger_event(self, 
        init_functions_framework, mounted_session):
        image_name = f"{uuid4()}.jpg"
        test_tz = datetime.datetime.now().isoformat()
        gcp_storage_msg = {'data': {
            'name': image_name,
            'bucket': 'output_bucket',
            'metageneration': '1',
            'timeCreated': test_tz,
            'updated': test_tz
            }
        }
        response = mounted_session.post(LOCAL_URL, json=gcp_storage_msg)
        return {"img": image_name, "response": response}

    # TODO: Fix this broken test once you've settled on correct gcp_storage_msg.
    def test_expected_response(self, trigger_event):
        assert trigger_event['response'].ok

    def test_downstream_image_uploaded(self, trigger_event):
        """Make sure downstream image storage upload method is called.
        """
        # TODO: finish test
        assert "mocked gcp storage method 'upload' for output bucket" == \
            "called with expected values"

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
        image_name = f"{uuid4()}.jpg"
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
