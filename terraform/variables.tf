variable "google_cloud_project" {
	type = string
}

variable "google_cloud_region" {
	type = string
	default = "asia-northeast1"
}

variable "docker_repository_id" {
    type = string
}

variable "gcs_log_bucket_name" {
    type = string
}

variable "bq_dataset_name" {
    type = string
    default = "family_data"
}