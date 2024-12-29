resource "google_cloud_run_v2_service" "sakamomo_family_api" {
  client         = "gcloud"
  client_version = "484.0.0"
  ingress        = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"
  launch_stage   = "GA"
  location       = var.google_cloud_region
  name           = "sakamomo-family-api"
  project        = var.google_cloud_project
  template {
    containers {
      env {
        name  = "LINE_CHANNEL_ACCESS_TOKEN"
        value = var.line_channel_access_token
      }
      env {
        name  = "LINE_CHANNEL_SECRET"
        value = var.line_channel_secret
      }
      env {
        name  = "OPEN_WEATHER_KEY"
        value = var.open_weather_key
      }
      env {
        name  = "OPENAI_API_KEY"
        value = var.openai_api_key
      }
      env {
        name  = "GCP_PROJECT"
        value = var.google_cloud_project
      }
      env {
        name  = "GCP_LOCATION"
        value = var.google_cloud_region
      }
      env {
        name  = "LANGCHAIN_ENDPOINT"
        value = var.langchain_endpoint
      }
      env {
        name  = "LANGCHAIN_API_KEY"
        value = var.langchain_api_key
      }
      env {
        name  = "LANGCHAIN_TRACING_V2"
        value = var.langchain_tracing_v2
      }
      env {
        name  = "GOOGLE_API_KEY"
        value = var.google_api_key
      }
      env {
        name  = "GOOGLE_CSE_ID"
        value = var.google_cse_id
      }
      env {
        name  = "EDINET_API_KEY"
        value = var.edinet_api_key
      }
      env {
        name  = "GCS_LOG_BUCKET_NAME"
        value = var.gcs_log_bucket_name
      }
      image = format("%s-docker.pkg.dev/%s/sakamomo-family-api/api", var.google_cloud_region, var.google_cloud_project)
      ports {
        container_port = 8080
        name           = "http1"
      }
      resources {
        cpu_idle = true
        limits = {
          cpu    = "1000m"
          memory = "512Mi"
        }
        startup_cpu_boost = true
      }
      startup_probe {
        failure_threshold     = 1
        initial_delay_seconds = 0
        period_seconds        = 240
        tcp_socket {
          port = 8080
        }
        timeout_seconds = 240
      }
    }
    max_instance_request_concurrency = 80
    scaling {
      max_instance_count = 100
    }
    service_account = google_service_account.service_api_backend.email
    timeout         = "300s"
  }
  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}

resource "google_cloud_run_v2_service" "sakamomo_family_web_app" {
  client         = "gcloud"
  client_version = "484.0.0"
  ingress        = "INGRESS_TRAFFIC_ALL"
  launch_stage   = "GA"
  location       = var.google_cloud_region
  name           = "sakamomo-family-web-app"
  project        = var.google_cloud_project
  template {
    containers {
      image = format("%s-docker.pkg.dev/%s/sakamomo-family-api/front", var.google_cloud_region, var.google_cloud_project)
      ports {
        container_port = 8501
        name           = "http1"
      }
      resources {
        cpu_idle = true
        limits = {
          cpu    = "1000m"
          memory = "512Mi"
        }
        startup_cpu_boost = true
      }
      startup_probe {
        failure_threshold     = 1
        initial_delay_seconds = 0
        period_seconds        = 240
        tcp_socket {
          port = 8501
        }
        timeout_seconds = 240
      }
    }
    max_instance_request_concurrency = 80
    scaling {
      max_instance_count = 100
    }
    service_account = google_service_account.service_web_frontend.email
    timeout         = "300s"
  }
  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}
