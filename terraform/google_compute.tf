resource "google_compute_global_address" "sakamomo_family_serivce_lb_ip" {
  address_type = "EXTERNAL"
  ip_version   = "IPV4"
  name         = "sakamomo-family-serivce-lb-ip"
  project      = var.google_cloud_project
}
