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

resource "google_bigquery_dataset" "family_data" {
  access {
    role          = "OWNER"
    special_group = "projectOwners"
  }
  access {
    role          = "READER"
    special_group = "projectReaders"
  }
  access {
    role          = "WRITER"
    special_group = "projectWriters"
  }
  dataset_id                 = var.bq_dataset_name
  delete_contents_on_destroy = false
  location                   = var.google_cloud_region
  max_time_travel_hours      = "168"
  project                    = var.google_cloud_project
}

resource "google_bigquery_table" "edinet_document_metadata" {
  project    = var.google_cloud_project
  dataset_id = var.bq_dataset_name
  schema     = "[{\"mode\":\"NULLABLE\",\"name\":\"seqNumber\",\"type\":\"INTEGER\"},{\"mode\":\"NULLABLE\",\"name\":\"docID\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"edinetCode\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"secCode\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"JCN\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"filerName\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"fundCode\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"ordinanceCode\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"formCode\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"docTypeCode\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"periodStart\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"periodEnd\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"submitDateTime\",\"type\":\"DATETIME\"},{\"mode\":\"NULLABLE\",\"name\":\"docDescription\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"issuerEdinetCode\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"subjectEdinetCode\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"subsidiaryEdinetCode\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"currentReportReason\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"parentDocID\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"opeDateTime\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"withdrawalStatus\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"docInfoEditStatus\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"disclosureStatus\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"xbrlFlag\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"pdfFlag\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"attachDocFlag\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"englishDocFlag\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"csvFlag\",\"type\":\"STRING\"},{\"mode\":\"NULLABLE\",\"name\":\"legalStatus\",\"type\":\"STRING\"}]"
  table_id   = "edinet_document_metadata"
}