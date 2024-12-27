provider "google" {
  project = var.google_cloud_project
  region  = var.google_cloud_region
}

resource "google_service_account" "service_deploy" {
  project      = var.google_cloud_project
  account_id   = "service-deploy"
  description  = "各サービスのデプロイやビルドを行うための管理用SA"
  display_name = "service-deploy"
}

variable "service_deploy_roles" {
  type = list(string)
  default = [
    "roles/editor",
    "roles/run.admin"
  ]
}

resource "google_project_iam_member" "service_deploy_iam" {
  for_each = toset(var.service_deploy_roles)
  project = var.google_cloud_project
  role    = each.value
  member  = "serviceAccount:${google_service_account.service_deploy.email}"
}

resource "google_service_account" "service_web_frontend" {
  project      = var.google_cloud_project
  account_id   = "service-web-frontend"
  description  = "WebFrontendのCloudRunに設定するSA"
  display_name = "service-web-frontend"
}

variable "service_web_frontend_roles" {
  type = list(string)
  default = [
    "roles/editor"
  ]
}

resource "google_project_iam_member" "service_web_frontend_iam" {
  for_each = toset(var.service_web_frontend_roles)
  project = var.google_cloud_project
  role    = each.value
  member  = "serviceAccount:${google_service_account.service_web_frontend.email}"
}

resource "google_service_account" "service_api_backend" {
  project      = var.google_cloud_project
  account_id   = "service-api-backend"
  description  = "WebFrontendのCloudRunに設定するSA"
  display_name = "service-api-backend"
}

variable "service_api_backend_roles" {
  type = list(string)
  default = [
    "roles/editor",
    "roles/storage.objectAdmin"
  ]
}

resource "google_project_iam_member" "service_api_backend_iam" {
  for_each = toset(var.service_api_backend_roles)
  project = var.google_cloud_project
  role    = each.value
  member  = "serviceAccount:${google_service_account.service_api_backend.email}"
}
