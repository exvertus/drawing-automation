import pytest
import subprocess
from os import getenv

PROJECT = getenv('GCP_PROJECT')
BUCKET = getenv('TEST_BUCKET')

class TestUnit:
    pass

class TestIntegration:
    pass

class TestSystem:
    """Tests that run against live system.
    """
    @pytest.fixture
    def deploy():
        subprocess.run(['./deploy.sh', BUCKET])

    def test_main():
        pass
