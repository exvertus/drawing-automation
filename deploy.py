import argparse
import shlex
import subprocess
from os import getenv

DEPLOYER_SA = getenv('GCP_FUNCTION_DEPLOYER_SA')
DEPLOYER_SA_KEY = getenv('GCP_FUNCTION_DEPLOYER_KEY')
RUNTIME = 'python310'
REGION = 'us-central1'
SA_CMD = "gcloud auth activate-service-account "\
    f"{DEPLOYER_SA} "
DEPLOY_CMD = "gcloud functions deploy process-public-images "\
    f"--gen2 --region={REGION} --runtime={RUNTIME} --quiet "\
    "--source=. --entry-point=process_public_images"

def login_as_service_account(key_file):
    # TODO: finish this
    pass

def deploy(trigger_bucket):
    command = f"{DEPLOY_CMD} --trigger-bucket={trigger_bucket}"
    print(command)
    args = shlex.split(command)
    return subprocess.run(args, shell=True, capture_output=True, check=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Deploy GCP Function')
    parser.add_argument('trigger', help='trigger-bucket for deployment')
    args = parser.parse_args()
    deploy(args.trigger)
