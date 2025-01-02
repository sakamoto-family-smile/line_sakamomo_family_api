resource "google_dns_managed_zone" "backend_service_com" {
  cloud_logging_config {
    enable_logging = false
  }
  description = "バックエンドサービスのdnsゾーン"
  dns_name    = format("%s.", google_clouddomains_registration.backend_service_domain.domain_name)
  dnssec_config {
    default_key_specs {
      algorithm  = "rsasha256"
      key_length = 2048
      key_type   = "keySigning"
      kind       = "dns#dnsKeySpec"
    }
    default_key_specs {
      algorithm  = "rsasha256"
      key_length = 1024
      key_type   = "zoneSigning"
      kind       = "dns#dnsKeySpec"
    }
    kind          = "dns#managedZoneDnsSecConfig"
    non_existence = "nsec3"
    state         = "on"
  }
  force_destroy = false
  name          = "sakamomo-family-service-com"
  project       = var.google_cloud_project
  visibility    = "public"
}

resource "google_dns_record_set" "A1" {
  name         = "@.${google_dns_managed_zone.backend_service_com.dns_name}."
  managed_zone = google_dns_managed_zone.backend_service_com.name
  type         = "A"
  ttl          = 300

  rrdatas = [google_compute_global_address.sakamomo_family_serivce_lb_ip.address]
}

resource "google_dns_record_set" "A2" {
  name         = "${google_dns_managed_zone.backend_service_com.dns_name}."
  managed_zone = google_dns_managed_zone.backend_service_com.name
  type         = "A"
  ttl          = 300

  rrdatas = [google_compute_global_address.sakamomo_family_serivce_lb_ip.address]
}
