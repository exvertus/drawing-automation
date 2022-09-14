# Image Automation

Cloud Function automated tasks for processing high-res images.

### One-time setup steps

```
SERVICE_ACCOUNT="$(gsutil kms serviceaccount -p PROJECT_ID)"

gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role='roles/pubsub.publisher'
```
* also give deploying service account service admin/agent roles for each cloud API used in the deployment:
  * Artifact Registry
  * Cloud Build
  * Cloud Functions
  * Container Registry
  * Pub/Sub Publisher
