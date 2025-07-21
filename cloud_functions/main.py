import json
import os

from google.cloud import storage


def store_json_to_gcs(event, context):
    """Triggered from a message on a Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.context.Context): Metadata for the event.
    """
    bucket_name = os.environ.get("GCS_BUCKET_NAME")
    if not bucket_name:
        print("GCS_BUCKET_NAME environment variable is not set.")
        return

    pubsub_message = event['data']
    if pubsub_message:
        try:
            json_data = json.loads(pubsub_message)
            client = storage.Client()
            bucket = client.get_bucket(bucket_name)
            blob = bucket.blob(f"pubsub_messages/{context.event_id}.json")
            blob.upload_from_string(
                data=json.dumps(json_data, indent=2),
                content_type="application/json"
            )
            print(f"JSON message stored to gs://{bucket_name}/pubsub_messages/{context.event_id}.json")
        except json.JSONDecodeError:
            print(f"Failed to decode JSON message: {pubsub_message}")
        except Exception as e:
            print(f"Error storing message to GCS: {e}")
    else:
        print("Pub/Sub message data is empty.")
