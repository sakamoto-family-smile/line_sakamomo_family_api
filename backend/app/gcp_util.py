from google.cloud import storage


def upload_file_into_gcs(project_id: str,
                         bucket_name: str,
                         remote_file_path: str,
                         local_file_path: str) -> str:
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(remote_file_path)
    blob.upload_from_filename(local_file_path, if_generation_match=0)
    return f"gs://{bucket_name}/{remote_file_path}"


def download_file_from_gcs(project_id: str,
                           bucket_name: str,
                           remote_file_path: str,
                           local_file_path: str):
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(remote_file_path)
    blob.download_to_filename(local_file_path)
