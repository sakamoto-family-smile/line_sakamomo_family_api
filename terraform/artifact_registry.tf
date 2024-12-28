resource "google_artifact_registry_repository" "sakamomo_family_api" {
  project                = var.google_cloud_project
  cleanup_policy_dry_run = true
  format                 = "DOCKER"
  location               = var.google_cloud_region
  mode                   = "STANDARD_REPOSITORY"
  repository_id          = var.docker_repository_id
}