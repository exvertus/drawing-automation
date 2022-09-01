# Drawing Automation

A collection of automation tasks run for each drawing in my portfolio.
All tasks are designed to:

- take an image/audio/video file and target-path as input
- process the file, things like...
  - format conversion
  - scaling/resizing
  - watermarking
  - metadata-obfuscation
- save the post-process artifact to GCP Cloud Storage
- idempotent for serverless environment
  - each task no-ops if its target storage path already exists
