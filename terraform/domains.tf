resource "google_clouddomains_registration" backend_service_domain {
  domain_name = format("%s.com", var.backend_service_domain_name)
  location    = "global"
  yearly_price {
    currency_code = "USD"
    units         = 12
  }
  dns_settings {
    custom_dns {
      name_servers = [
        "ns-cloud-a1.googledomains.com.",
        "ns-cloud-a2.googledomains.com.",
        "ns-cloud-a3.googledomains.com.",
        "ns-cloud-a4.googledomains.com."
      ]
    }
  }
  contact_settings {
    privacy = "REDACTED_CONTACT_DATA"
    registrant_contact {
      phone_number = var.backend_service_domain_phone_number
      email        = var.backend_service_domain_email
      postal_address {
        region_code         = var.backend_service_domain_postal_address["region_code"]
        postal_code         = var.backend_service_domain_postal_address["postal_code"]
        administrative_area = var.backend_service_domain_postal_address["administrative_area"]
        locality            = var.backend_service_domain_postal_address["locality"]
        address_lines       = [var.backend_service_domain_postal_address["address_line"]]
        recipients          = [var.backend_service_domain_postal_address["recipient"]]
      }
    }
    admin_contact {
      phone_number = var.backend_service_domain_phone_number
      email        = var.backend_service_domain_email
      postal_address {
        region_code         = var.backend_service_domain_postal_address["region_code"]
        postal_code         = var.backend_service_domain_postal_address["postal_code"]
        administrative_area = var.backend_service_domain_postal_address["administrative_area"]
        locality            = var.backend_service_domain_postal_address["locality"]
        address_lines       = [var.backend_service_domain_postal_address["address_line"]]
        recipients          = [var.backend_service_domain_postal_address["recipient"]]
      }
    }
    technical_contact {
      phone_number = var.backend_service_domain_phone_number
      email        = var.backend_service_domain_email
      postal_address {
        region_code         = var.backend_service_domain_postal_address["region_code"]
        postal_code         = var.backend_service_domain_postal_address["postal_code"]
        administrative_area = var.backend_service_domain_postal_address["administrative_area"]
        locality            = var.backend_service_domain_postal_address["locality"]
        address_lines       = [var.backend_service_domain_postal_address["address_line"]]
        recipients          = [var.backend_service_domain_postal_address["recipient"]]
      }
    }
  }
}