variable "use_gcp_service_list" {
  type    = list(string)
  default = [
    "aiplatform.googleapis.com",
    "artifactregistry.googleapis.com",
    "run.googleapis.com",
    "datastore.googleapis.com", # for Firestore
    "cloudscheduler.googleapis.com",
    "identitytoolkit.googleapis.com",
    "iap.googleapis.com",
    "domains.googleapis.com"
  ]
}

resource "google_project_service" "gcp_service_apis" {
  for_each = toset(var.use_gcp_service_list)

  project = var.google_cloud_project
  service = each.key
  disable_on_destroy = false
}
