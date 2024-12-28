resource "google_firestore_database" "api_database" {
  project                           = var.google_cloud_project
  name                              = "(default)"
  location_id                       = var.google_cloud_region
  type                              = "FIRESTORE_NATIVE"
}

resource "google_storage_bucket" "sakamomo_family_service_log" {
  project                     = var.google_cloud_project
  force_destroy               = false
  location                    = var.google_cloud_region
  name                        = var.gcs_log_bucket_name
  public_access_prevention    = "enforced"
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
}
