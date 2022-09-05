#!/bin/bash
gcloud functions deploy pub_proc_image \
--gen2 \
--runtime=python310 \
--source=. \
--trigger-bucket=$1 \
--quiet