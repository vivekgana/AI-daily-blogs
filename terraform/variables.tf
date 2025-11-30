# Terraform Variables for AGI Research Platform

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "gemini_api_key_secret" {
  description = "Secret Manager secret name for Gemini API key"
  type        = string
  default     = "gemini-api-key"
}

variable "anthropic_api_key_secret" {
  description = "Secret Manager secret name for Anthropic API key"
  type        = string
  default     = "anthropic-api-key"
}

variable "kaggle_username_secret" {
  description = "Secret Manager secret name for Kaggle username"
  type        = string
  default     = "kaggle-username"
}

variable "kaggle_key_secret" {
  description = "Secret Manager secret name for Kaggle API key"
  type        = string
  default     = "kaggle-key"
}

variable "min_collector_instances" {
  description = "Minimum instances for data collector service"
  type        = number
  default     = 1
}

variable "max_collector_instances" {
  description = "Maximum instances for data collector service"
  type        = number
  default     = 50
}

variable "min_reasoning_instances" {
  description = "Minimum instances for reasoning engine service"
  type        = number
  default     = 0
}

variable "max_reasoning_instances" {
  description = "Maximum instances for reasoning engine service"
  type        = number
  default     = 20
}

variable "min_api_instances" {
  description = "Minimum instances for API service"
  type        = number
  default     = 2
}

variable "max_api_instances" {
  description = "Maximum instances for API service"
  type        = number
  default     = 100
}

variable "data_retention_days" {
  description = "Days to retain raw data before deletion"
  type        = number
  default     = 90
}

variable "enable_monitoring" {
  description = "Enable Cloud Monitoring and Logging"
  type        = bool
  default     = true
}

variable "enable_backups" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}

variable "collection_schedule" {
  description = "Cron schedule for data collection"
  type        = string
  default     = "0 */6 * * *"  # Every 6 hours
}

variable "report_schedule" {
  description = "Cron schedule for daily reports"
  type        = string
  default     = "0 8 * * *"  # 8 AM EST
}

variable "labels" {
  description = "Labels to apply to all resources"
  type        = map(string)
  default     = {
    project     = "agi-research"
    managed_by  = "terraform"
  }
}
