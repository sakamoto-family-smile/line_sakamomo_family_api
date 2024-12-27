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
