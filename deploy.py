import argparse
import shlex
import subprocess

RUNTIME = 'python310'
REGION = 'us-central1'
DEPLOY_CMD = "gcloud functions deploy imagefunc "\
    f"--gen2 --region={REGION} --runtime={RUNTIME} --source=. --quiet"

def deploy(trigger_bucket):
    command = f"{DEPLOY_CMD} --trigger-bucket={trigger_bucket}"
    print(command)
    args = shlex.split(command)
    return subprocess.wait(args, shell=True, capture_output=True, check=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Deploy GCP Function')
    parser.add_argument('trigger', help='trigger-bucket for deployment')
    args = parser.parse_args()
    deploy(args.trigger)
