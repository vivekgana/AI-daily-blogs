# Main Terraform Configuration for AGI Research Platform

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }

  backend "gcs" {
    bucket = "agi-research-terraform-state"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",
    "cloudfunctions.googleapis.com",
    "storage.googleapis.com",
    "firestore.googleapis.com",
    "bigquery.googleapis.com",
    "pubsub.googleapis.com",
    "cloudscheduler.googleapis.com",
    "secretmanager.googleapis.com",
    "aiplatform.googleapis.com",
    "compute.googleapis.com",
    "vpcaccess.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com"
  ])

  service            = each.key
  disable_on_destroy = false
}

# Local values
locals {
  common_labels = merge(
    var.labels,
    {
      environment = var.environment
    }
  )

  bucket_prefix = "${var.project_id}-${var.environment}"
}

# Cloud Storage Buckets
resource "google_storage_bucket" "raw_data" {
  name          = "${local.bucket_prefix}-raw-data"
  location      = var.region
  storage_class = "STANDARD"

  uniform_bucket_level_access = true

  labels = local.common_labels

  lifecycle_rule {
    condition {
      age = var.data_retention_days
    }
    action {
      type = "Delete"
    }
  }

  lifecycle_rule {
    condition {
      age = 30
      matches_prefix = ["temp/"]
    }
    action {
      type = "Delete"
    }
  }

  versioning {
    enabled = var.enable_backups
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_storage_bucket" "processed_data" {
  name          = "${local.bucket_prefix}-processed-data"
  location      = var.region
  storage_class = "STANDARD"

  uniform_bucket_level_access = true

  labels = local.common_labels

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  lifecycle_rule {
    condition {
      age = 180
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }

  versioning {
    enabled = var.enable_backups
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_storage_bucket" "models" {
  name          = "${local.bucket_prefix}-models"
  location      = var.region
  storage_class = "STANDARD"

  uniform_bucket_level_access = true

  labels = local.common_labels

  versioning {
    enabled = true
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_storage_bucket" "backups" {
  name          = "${local.bucket_prefix}-backups"
  location      = "US"  # Multi-region for backups
  storage_class = "ARCHIVE"

  uniform_bucket_level_access = true

  labels = local.common_labels

  lifecycle_rule {
    condition {
      age = 365  # Keep backups for 1 year
    }
    action {
      type = "Delete"
    }
  }

  depends_on = [google_project_service.required_apis]
}

# Pub/Sub Topics
resource "google_pubsub_topic" "research_raw" {
  name = "agi-research-raw"

  labels = local.common_labels

  message_retention_duration = "604800s"  # 7 days

  depends_on = [google_project_service.required_apis]
}

resource "google_pubsub_topic" "research_processed" {
  name = "agi-research-processed"

  labels = local.common_labels

  message_retention_duration = "86400s"  # 1 day

  depends_on = [google_project_service.required_apis]
}

resource "google_pubsub_topic" "research_alerts" {
  name = "agi-research-alerts"

  labels = local.common_labels

  message_retention_duration = "86400s"  # 1 day

  depends_on = [google_project_service.required_apis]
}

resource "google_pubsub_topic" "dead_letter" {
  name = "agi-research-dead-letter"

  labels = local.common_labels

  message_retention_duration = "604800s"  # 7 days

  depends_on = [google_project_service.required_apis]
}

# Pub/Sub Subscriptions
resource "google_pubsub_subscription" "reasoning_engine_sub" {
  name  = "reasoning-engine-subscription"
  topic = google_pubsub_topic.research_raw.name

  ack_deadline_seconds = 600

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dead_letter.id
    max_delivery_attempts = 5
  }

  labels = local.common_labels

  depends_on = [google_project_service.required_apis]
}

resource "google_pubsub_subscription" "alerts_sub" {
  name  = "alerts-subscription"
  topic = google_pubsub_topic.research_alerts.name

  ack_deadline_seconds = 300

  push_config {
    push_endpoint = "${google_cloud_run_service.api_service.status[0].url}/webhooks/alerts"

    oidc_token {
      service_account_email = google_service_account.pubsub_invoker.email
    }
  }

  labels = local.common_labels

  depends_on = [google_project_service.required_apis]
}

# Firestore Database
resource "google_firestore_database" "agi_research" {
  provider = google-beta

  name        = "(default)"
  location_id = "nam5"
  type        = "FIRESTORE_NATIVE"

  depends_on = [google_project_service.required_apis]
}

# BigQuery Dataset
resource "google_bigquery_dataset" "agi_analytics" {
  dataset_id                 = "agi_research_analytics"
  location                   = "US"
  default_table_expiration_ms = null

  labels = local.common_labels

  access {
    role          = "OWNER"
    user_by_email = google_service_account.reasoning_engine.email
  }

  access {
    role          = "READER"
    user_by_email = google_service_account.api_service.email
  }

  depends_on = [google_project_service.required_apis]
}

# BigQuery Tables
resource "google_bigquery_table" "research_papers" {
  dataset_id = google_bigquery_dataset.agi_analytics.dataset_id
  table_id   = "research_papers"

  time_partitioning {
    type  = "DAY"
    field = "published_date"
  }

  clustering = ["agi_relevance_score", "asi_relevance_score"]

  labels = local.common_labels

  schema = file("${path.module}/../gcp/schemas/research_papers.json")
}

resource "google_bigquery_table" "trends_analysis" {
  dataset_id = google_bigquery_dataset.agi_analytics.dataset_id
  table_id   = "trends_analysis"

  time_partitioning {
    type  = "DAY"
    field = "start_date"
  }

  labels = local.common_labels

  schema = file("${path.module}/../gcp/schemas/trends_analysis.json")
}

resource "google_bigquery_table" "daily_metrics" {
  dataset_id = google_bigquery_dataset.agi_analytics.dataset_id
  table_id   = "daily_metrics"

  time_partitioning {
    type  = "DAY"
    field = "metric_date"
  }

  labels = local.common_labels

  schema = file("${path.module}/../gcp/schemas/daily_metrics.json")
}

# Service Accounts
resource "google_service_account" "data_collector" {
  account_id   = "agi-data-collector"
  display_name = "AGI Data Collector Service Account"
}

resource "google_service_account" "reasoning_engine" {
  account_id   = "agi-reasoning-engine"
  display_name = "AGI Reasoning Engine Service Account"
}

resource "google_service_account" "api_service" {
  account_id   = "agi-api-service"
  display_name = "AGI API Service Account"
}

resource "google_service_account" "scheduler" {
  account_id   = "agi-scheduler"
  display_name = "AGI Cloud Scheduler Service Account"
}

resource "google_service_account" "pubsub_invoker" {
  account_id   = "agi-pubsub-invoker"
  display_name = "AGI Pub/Sub Invoker Service Account"
}

# IAM Bindings for Data Collector
resource "google_storage_bucket_iam_member" "collector_raw_data" {
  bucket = google_storage_bucket.raw_data.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.data_collector.email}"
}

resource "google_pubsub_topic_iam_member" "collector_publisher" {
  topic  = google_pubsub_topic.research_raw.name
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:${google_service_account.data_collector.email}"
}

resource "google_project_iam_member" "collector_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.data_collector.email}"
}

# IAM Bindings for Reasoning Engine
resource "google_storage_bucket_iam_member" "reasoning_raw_data" {
  bucket = google_storage_bucket.raw_data.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.reasoning_engine.email}"
}

resource "google_storage_bucket_iam_member" "reasoning_processed_data" {
  bucket = google_storage_bucket.processed_data.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.reasoning_engine.email}"
}

resource "google_pubsub_subscription_iam_member" "reasoning_subscriber" {
  subscription = google_pubsub_subscription.reasoning_engine_sub.name
  role         = "roles/pubsub.subscriber"
  member       = "serviceAccount:${google_service_account.reasoning_engine.email}"
}

resource "google_pubsub_topic_iam_member" "reasoning_publisher" {
  topic  = google_pubsub_topic.research_processed.name
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:${google_service_account.reasoning_engine.email}"
}

resource "google_project_iam_member" "reasoning_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.reasoning_engine.email}"
}

resource "google_project_iam_member" "reasoning_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.reasoning_engine.email}"
}

resource "google_project_iam_member" "reasoning_firestore_user" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.reasoning_engine.email}"
}

# IAM Bindings for API Service
resource "google_storage_bucket_iam_member" "api_processed_data" {
  bucket = google_storage_bucket.processed_data.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.api_service.email}"
}

resource "google_project_iam_member" "api_firestore_user" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.api_service.email}"
}

resource "google_bigquery_dataset_iam_member" "api_bigquery_reader" {
  dataset_id = google_bigquery_dataset.agi_analytics.dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = "serviceAccount:${google_service_account.api_service.email}"
}

# Cloud Run Services
resource "google_cloud_run_service" "data_collector" {
  name     = "agi-data-collector"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.data_collector.email

      containers {
        image = "gcr.io/${var.project_id}/agi-data-collector:latest"

        resources {
          limits = {
            cpu    = "2000m"
            memory = "4Gi"
          }
        }

        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }

        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }

        env {
          name = "KAGGLE_USERNAME"
          value_from {
            secret_key_ref {
              name = var.kaggle_username_secret
              key  = "latest"
            }
          }
        }

        env {
          name = "KAGGLE_KEY"
          value_from {
            secret_key_ref {
              name = var.kaggle_key_secret
              key  = "latest"
            }
          }
        }
      }

      container_concurrency = 100
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = var.min_collector_instances
        "autoscaling.knative.dev/maxScale" = var.max_collector_instances
      }

      labels = local.common_labels
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_cloud_run_service" "reasoning_engine" {
  name     = "agi-reasoning-engine"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.reasoning_engine.email
      timeout_seconds      = 3600  # 1 hour for complex reasoning

      containers {
        image = "gcr.io/${var.project_id}/agi-reasoning-engine:latest"

        resources {
          limits = {
            cpu    = "4000m"
            memory = "8Gi"
          }
        }

        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }

        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }

        env {
          name = "GEMINI_API_KEY"
          value_from {
            secret_key_ref {
              name = var.gemini_api_key_secret
              key  = "latest"
            }
          }
        }

        env {
          name = "ANTHROPIC_API_KEY"
          value_from {
            secret_key_ref {
              name = var.anthropic_api_key_secret
              key  = "latest"
            }
          }
        }
      }

      container_concurrency = 10  # Lower due to resource-intensive operations
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = var.min_reasoning_instances
        "autoscaling.knative.dev/maxScale" = var.max_reasoning_instances
      }

      labels = local.common_labels
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_cloud_run_service" "api_service" {
  name     = "agi-api-service"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.api_service.email

      containers {
        image = "gcr.io/${var.project_id}/agi-api-service:latest"

        resources {
          limits = {
            cpu    = "2000m"
            memory = "2Gi"
          }
        }

        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }

        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }

        ports {
          container_port = 8080
        }
      }

      container_concurrency = 200
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = var.min_api_instances
        "autoscaling.knative.dev/maxScale" = var.max_api_instances
      }

      labels = local.common_labels
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [google_project_service.required_apis]
}

# Cloud Run IAM for public access (API service only)
resource "google_cloud_run_service_iam_member" "api_public_access" {
  service  = google_cloud_run_service.api_service.name
  location = google_cloud_run_service.api_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Cloud Run IAM for scheduler
resource "google_cloud_run_service_iam_member" "collector_scheduler_invoker" {
  service  = google_cloud_run_service.data_collector.name
  location = google_cloud_run_service.data_collector.location
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.scheduler.email}"
}

resource "google_cloud_run_service_iam_member" "reasoning_scheduler_invoker" {
  service  = google_cloud_run_service.reasoning_engine.name
  location = google_cloud_run_service.reasoning_engine.location
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.scheduler.email}"
}

# Cloud Scheduler Jobs
resource "google_cloud_scheduler_job" "data_collection" {
  name        = "agi-data-collection"
  description = "Trigger AGI research data collection"
  schedule    = var.collection_schedule
  time_zone   = "America/New_York"
  region      = var.region

  http_target {
    http_method = "POST"
    uri         = "${google_cloud_run_service.data_collector.status[0].url}/collect"

    oidc_token {
      service_account_email = google_service_account.scheduler.email
    }
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_cloud_scheduler_job" "daily_report" {
  name        = "agi-daily-report"
  description = "Generate daily AGI research report"
  schedule    = var.report_schedule
  time_zone   = "America/New_York"
  region      = var.region

  http_target {
    http_method = "POST"
    uri         = "${google_cloud_run_service.reasoning_engine.status[0].url}/generate-report"

    oidc_token {
      service_account_email = google_service_account.scheduler.email
    }
  }

  depends_on = [google_project_service.required_apis]
}
