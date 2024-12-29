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

variable "line_channel_access_token" {
    type = string
}

variable "line_channel_secret" {
    type = string
}

variable "open_weather_key" {
    type = string
}

variable "openai_api_key" {
    type = string
}

variable "langchain_endpoint" {
    type = string
}

variable "langchain_api_key" {
    type = string
}

variable "langchain_tracing_v2" {
    type = string  # これ文字列で良いのか？
}

variable "google_api_key" {
    type = string
}

variable "google_cse_id" {
    type = string
}

variable "edinet_api_key" {
    type = string
}

variable "backend_service_domain_name" {
    type = string
}

variable "backend_service_domain_phone_number" {
    type = string
}

variable "backend_service_domain_email" {
    type = string
}

variable "backend_service_domain_postal_address" {
    type = map(any)
    default = {
        region_code         = ""
        postal_code         = ""
        administrative_area = ""
        locality            = ""
        address_line        = "" # TODO : リスト形式で設定する必要がある
        recipient           = "" # TODO : リスト形式で設定する必要がある
    }
}