import datetime
from enum import auto
from tkinter import image_names
from unittest import mock
import pytest
import shlex
import shutil
import subprocess
import requests
import time
from os import getenv
from pathlib import Path
from uuid import uuid4

from cloudevents.http import CloudEvent

import deploy
import main

PROJECT = getenv('GCP_PROJECT')
TEST_INPUT_BUCKET = getenv('TEST_INPUT_BUCKET')
TEST_OUTPUT_BUCKET = getenv('TEST_OUTPUT_BUCKET')
LOCAL_PORT = 8099
LOCAL_URL = f"http://localhost:{LOCAL_PORT}/"
FINALIZED_EVENT_TYPE = "google.cloud.storage.object.v1.finalized"

@pytest.fixture(params=main.MAX_DIMENSIONS.items())
def fanout_by_dimensions(request):
    return request.param

@pytest.fixture()
def random_jpeg_name():
    return f"{uuid4()}.jpg"

@pytest.fixture()
def patch_pillow(mocker):
    mocker.patch('PIL')

@pytest.fixture(scope='class')
def patch_storage(class_mocker):
    class_mocker.patch('main.storage')

class TestUnit:
    @pytest.fixture(scope='class')
    def mock_client(self, class_mocker):
        client = class_mocker.MagicMock(
            autospec=main.storage.Client, 
            name='storage_client')
        class_mocker.patch('main.storage.Client', new=client)
        return client

    @pytest.mark.skip(reason='TODO')
    def test_create_smaller_copies(self, patch_pillow):
        image_path = Path()
        main.create_smaller_copies(image_path)
        assert "TODO" == "done."

    def test_storage_client(self, monkeypatch, mock_client):
        monkeypatch.setattr(main, "gcp_storage_client", None)
        first = main.storage_client()
        second = main.storage_client()
        assert (first is second) and (mock_client.call_count == 1)

    def test_download_image(self, mock_client):
        main.download_image('test_bucket', 'test_blob_name')
        mock_client.return_value.download_blob_to_file.assert_called()

    def test_create_smaller_copies(self):
        assert "todo" == "done"

class TestIntegrationPillow:
    """'Narrow' integration tests: PIL
    """
    @pytest.fixture(scope='class', autouse=True)
    def mock_event(self, class_mocker):
        mocked_event = class_mocker.Mock(autospec=CloudEvent)
        mocked_event.__getitem__ = class_mocker.Mock()
        # https://cloud.google.com/python/docs/reference/storage/latest/google.cloud.storage.blob.Blob
        mocked_event.data = {
            "bucket": "test_bucket_for_storage",
            "name": "tests/test.jpg",
            "generation": 1,
            "metageneration": 1,
            "timeCreated": "2021-10-10 00:00:00.000000Z",
            "updated": "2021-11-11 00:00:00.000000Z",
        }
        return mocked_event

    @pytest.fixture(scope='class', autouse=True)
    def patch_download_image(self, class_mocker):
        class_mocker.patch(
            'main.download_image', 
            return_value=Path('.') / 'tests/test.jpg')

    @pytest.fixture(scope='class')
    def process_image(self, mock_event, patch_storage):
        main.process_public_images(mock_event)
        return mock_event.data["name"]

    @pytest.fixture()
    def downstream_image(self, process_image, fanout_by_dimensions):
        from PIL import Image
        dimension_name = fanout_by_dimensions[0]
        max_dimension = fanout_by_dimensions[1]
        expected_path = Path(__file__).parents[1] /\
            main.blob_name(process_image, dimension_name)
        downstream_image = Image.open(expected_path)
        return {
            'max_dimension': max_dimension,
            'longest_dimension': max(downstream_image.size)
        }

    def test_size_upper_bound(self, downstream_image):
        """Make sure resizing result is no larger than expected.
        """
        assert downstream_image['longest_dimension'] <= \
            downstream_image['max_dimension']

    def test_size_lower_bound(self, downstream_image):
        """Make sure resizing result is no smaller than next size down.
        """
        sizes = main.MAX_DIMENSIONS.values().sort().insert(0, 0)
        position = sizes.find(downstream_image['max_dim']) - 1
        expected_min = sizes[position]
        assert downstream_image['longest_dim'] > expected_min

class TestIntegrationFuncFW:
    """'Narrow' integration tests: functions-framework
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

    @pytest.fixture()
    def trigger_event(
        self, init_functions_framework, random_jpeg_name, monkeypatch):
        event_attrs = {
            "id": "5555555",
            "type": FINALIZED_EVENT_TYPE,
        }
        event_data = {
            "bucket": "test_bucket_for_storage",
            "name": "new_blob_uploaded",
            "generation": 1,
            "metageneration": 1,
            "timeCreated": "2021-10-10 00:00:00.000000Z",
            "updated": "2021-11-11 00:00:00.000000Z",
        }
        cloud_event = CloudEvent(event_attrs, event_data)

        return main.process_public_images(cloud_event)

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
        from google.cloud import storage
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
    def upload_test_image(self, input_bucket, random_jpeg_name):
        image_name = random_jpeg_name
        blob = input_bucket.blob(image_name)
        blob.upload_from_filename(Path("./tests/test.jpg"))
        # Wait for Function call from upload to complete.
        time.sleep(45)

        yield image_name

        for size in main.MAX_DIMENSIONS:
            ds_blob = main.blob_name(image_name, size)
        blob.delete()

    def test_image_exists(
        self, input_bucket, upload_test_image, fanout_by_dimensions):
        image = upload_test_image
        dimension_name = fanout_by_dimensions[0]
        max_dimension = fanout_by_dimensions[1]
        assert input_bucket.blob(image).exists()

    def test_expected_dimensions(self):
        assert "expected_dimensions"

    @pytest.mark.skip(reason="TODO")
    def test_exif_wiped(self):
        assert "exif_wiped"

    @pytest.mark.skip(reason="TODO")
    def test_watermark_added(self):
        assert "watermark_added"
    
    @pytest.mark.skip(reason="TODO")
    def test_record_updated(self):
        assert "record_updated"
