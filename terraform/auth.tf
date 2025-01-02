resource "google_identity_platform_project_default_config" "default" {
  project = var.google_cloud_project

  sign_in {
    email {
      enabled = true
      password_required = true
    }
  }
}
