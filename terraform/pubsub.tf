resource "google_pubsub_topic" "pubsub_topic" {
  name = "json-message-topic"
}

resource "google_pubsub_subscription" "pubsub_subscription" {
  name  = "cloud-functions-subscription"
  topic = google_pubsub_topic.pubsub_topic.name
}
