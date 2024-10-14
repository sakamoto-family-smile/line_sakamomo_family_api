from typing import List

from google.cloud import storage


def upload_file_into_gcs(project_id: str, bucket_name: str, remote_file_path: str, local_file_path: str) -> str:
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(remote_file_path)
    blob.upload_from_filename(local_file_path, if_generation_match=0)
    return f"gs://{bucket_name}/{remote_file_path}"


def download_file_from_gcs(project_id: str, bucket_name: str, remote_file_path: str, local_file_path: str):
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(remote_file_path)
    blob.download_to_filename(local_file_path)


def split_bucket_name_and_file_path(gcs_uri: str) -> List[str]:
    uri = gcs_uri.replace("gs://", "")
    return uri.split("/", 1)


def get_filename_from_gcs_uri(gcs_uri: str) -> str:
    return gcs_uri.split("/")[-1]
