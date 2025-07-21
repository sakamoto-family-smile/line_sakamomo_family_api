resource "google_cloudfunctions_function" "cloud_function" {
  name                  = "pubsub-to-gcs-function"
  region                = "asia-northeast1" # Replace with your desired region
  entry_point           = "store_json_to_gcs"
  runtime               = "python310" # Choose an appropriate Python runtime
  available_memory_mb   = 128
  timeout               = 60

  source_archive_bucket = "sakamomo_family_service" # Replace with your staging bucket
  source_archive_object = "client_log_cf.zip" # You'll need to upload the zipped source code

  trigger_http = false
  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = google_pubsub_topic.pubsub_topic.name
  }
  environment_variables = {
    GCS_BUCKET_NAME = "sakamomo_family_service" # Replace with your GCS bucket name
  }
}
