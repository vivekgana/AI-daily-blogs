# Terraform Outputs

output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP Region"
  value       = var.region
}

output "environment" {
  description = "Environment name"
  value       = var.environment
}

# Storage Buckets
output "raw_data_bucket" {
  description = "Raw data bucket name"
  value       = google_storage_bucket.raw_data.name
}

output "processed_data_bucket" {
  description = "Processed data bucket name"
  value       = google_storage_bucket.processed_data.name
}

output "models_bucket" {
  description = "Models bucket name"
  value       = google_storage_bucket.models.name
}

output "backups_bucket" {
  description = "Backups bucket name"
  value       = google_storage_bucket.backups.name
}

# Pub/Sub Topics
output "research_raw_topic" {
  description = "Research raw data topic"
  value       = google_pubsub_topic.research_raw.name
}

output "research_processed_topic" {
  description = "Research processed data topic"
  value       = google_pubsub_topic.research_processed.name
}

# BigQuery
output "bigquery_dataset" {
  description = "BigQuery analytics dataset"
  value       = google_bigquery_dataset.agi_analytics.dataset_id
}

# Cloud Run Services
output "data_collector_url" {
  description = "Data Collector service URL"
  value       = google_cloud_run_service.data_collector.status[0].url
}

output "reasoning_engine_url" {
  description = "Reasoning Engine service URL"
  value       = google_cloud_run_service.reasoning_engine.status[0].url
}

output "api_service_url" {
  description = "API service URL"
  value       = google_cloud_run_service.api_service.status[0].url
}

# Service Accounts
output "data_collector_sa_email" {
  description = "Data Collector service account email"
  value       = google_service_account.data_collector.email
}

output "reasoning_engine_sa_email" {
  description = "Reasoning Engine service account email"
  value       = google_service_account.reasoning_engine.email
}

output "api_service_sa_email" {
  description = "API service account email"
  value       = google_service_account.api_service.email
}

# Scheduler Jobs
output "collection_schedule" {
  description = "Data collection schedule"
  value       = google_cloud_scheduler_job.data_collection.schedule
}

output "report_schedule" {
  description = "Daily report generation schedule"
  value       = google_cloud_scheduler_job.daily_report.schedule
}
