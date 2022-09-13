import argparse
import subprocess

def deploy(trigger_bucket):
    return subprocess.run([
        "gcloud functions deploy pub_proc_image",
        "--gen2",
        "--runtime=python310",
        "--source=.",
        "--trigger-bucket={trigger_bucket}",
        "--quiet"
    ])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Deploy GCP Function')
    parser.add_argument('trigger', help='trigger-bucket for deployment')
    args = parser.parse_args()
    deploy(args.trigger)
