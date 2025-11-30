# AGI/ASI Research Platform - Deployment Guide

## Quick Start Deployment

### Prerequisites

1. **GCP Account** with billing enabled
2. **Required Tools:**
   - `gcloud` CLI (v400.0.0+)
   - `terraform` (v1.5.0+)
   - `docker` (v20.10+)
   - `git`

3. **API Keys:**
   - Google Gemini API key
   - Anthropic Claude API key
   - Kaggle API credentials (optional for integration)

### Step 1: Initial GCP Setup

```bash
# Set your project ID
export PROJECT_ID="your-agi-research-project"
export REGION="us-central1"

# Authenticate with GCP
gcloud auth login
gcloud config set project $PROJECT_ID

# Enable required APIs (automated in Terraform)
gcloud services enable \
  run.googleapis.com \
  storage.googleapis.com \
  firestore.googleapis.com \
  bigquery.googleapis.com \
  pubsub.googleapis.com \
  aiplatform.googleapis.com \
  secretmanager.googleapis.com
```

### Step 2: Store API Keys in Secret Manager

```bash
# Store Gemini API Key
echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets create gemini-api-key \
  --data-file=- \
  --replication-policy="automatic"

# Store Anthropic API Key
echo -n "YOUR_ANTHROPIC_API_KEY" | gcloud secrets create anthropic-api-key \
  --data-file=- \
  --replication-policy="automatic"

# Store Kaggle credentials (optional)
echo -n "YOUR_KAGGLE_USERNAME" | gcloud secrets create kaggle-username \
  --data-file=- \
  --replication-policy="automatic"

echo -n "YOUR_KAGGLE_KEY" | gcloud secrets create kaggle-key \
  --data-file=- \
  --replication-policy="automatic"
```

### Step 3: Deploy Infrastructure with Terraform

```bash
# Navigate to terraform directory
cd terraform

# Create Terraform state bucket
gsutil mb gs://agi-research-terraform-state

# Initialize Terraform
terraform init

# Create a terraform.tfvars file
cat > terraform.tfvars << EOF
project_id  = "${PROJECT_ID}"
region      = "${REGION}"
environment = "prod"
EOF

# Plan deployment
terraform plan -out=tfplan

# Apply infrastructure
terraform apply tfplan
```

### Step 4: Build and Deploy Services

```bash
# Navigate back to project root
cd ..

# Submit build to Cloud Build
gcloud builds submit \
  --config=gcp/cloudbuild/cloudbuild.yaml \
  --substitutions=_DEPLOY_ENV=prod

# This will:
# - Build Docker images for all services
# - Push images to Container Registry
# - Deploy to Cloud Run
# - Run smoke tests
```

### Step 5: Verify Deployment

```bash
# Get service URLs
DATA_COLLECTOR_URL=$(gcloud run services describe agi-data-collector \
  --region=$REGION --format='value(status.url)')

REASONING_ENGINE_URL=$(gcloud run services describe agi-reasoning-engine \
  --region=$REGION --format='value(status.url)')

API_URL=$(gcloud run services describe agi-api-service \
  --region=$REGION --format='value(status.url)')

echo "Data Collector: $DATA_COLLECTOR_URL"
echo "Reasoning Engine: $REASONING_ENGINE_URL"
echo "API Service: $API_URL"

# Test API service (publicly accessible)
curl $API_URL/health
```

### Step 6: Trigger First Data Collection

```bash
# Get a token for authenticated request
TOKEN=$(gcloud auth print-identity-token)

# Manually trigger data collection
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  $DATA_COLLECTOR_URL/collect

# This will start collecting AGI research papers
```

### Step 7: Monitor System

```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision" \
  --limit=50 \
  --format=json

# View metrics in Cloud Console
echo "Monitoring Dashboard:"
echo "https://console.cloud.google.com/monitoring/dashboards?project=$PROJECT_ID"

# View BigQuery data
echo "BigQuery Console:"
echo "https://console.cloud.google.com/bigquery?project=$PROJECT_ID"
```

## Configuration

### Environment Variables

All services use these environment variables:

- `PROJECT_ID`: GCP project ID
- `ENVIRONMENT`: Environment name (dev/staging/prod)
- `GEMINI_API_KEY`: Google Gemini API key (from Secret Manager)
- `ANTHROPIC_API_KEY`: Anthropic Claude API key (from Secret Manager)

### Scheduled Collection

Data collection runs automatically:
- **Schedule**: Every 6 hours (configurable in `terraform/variables.tf`)
- **Cron**: `0 */6 * * *`
- **Timezone**: America/New_York

Daily reports generate:
- **Schedule**: Daily at 8 AM EST
- **Cron**: `0 8 * * *`

## Cost Optimization

### Estimated Monthly Costs

- **Cloud Run**: $500-1,500
- **Cloud Storage**: $150-300
- **BigQuery**: $150-300
- **Firestore**: $150-300
- **AI APIs (Gemini/Claude)**: $1,500-4,000
- **Total**: ~$2,500-6,500/month

### Cost Reduction Tips

1. **Adjust collection frequency** - Reduce from 6-hour to daily
2. **Use Gemini Flash** instead of Pro for simple tasks
3. **Implement caching** for embeddings and analysis results
4. **Set max instances lower** during low-traffic periods
5. **Archive old data** to Coldline storage

## Monitoring & Alerts

### Key Metrics to Monitor

1. **Collection Success Rate**
   ```sql
   SELECT
     DATE(metric_date) as date,
     SUM(papers_collected) as total_papers,
     AVG(processing_time_seconds) as avg_time
   FROM `agi_research_analytics.daily_metrics`
   GROUP BY date
   ORDER BY date DESC
   LIMIT 30
   ```

2. **API Costs**
   ```sql
   SELECT
     metric_date,
     api_costs,
     papers_analyzed
   FROM `agi_research_analytics.daily_metrics`
   WHERE metric_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
   ORDER BY metric_date DESC
   ```

3. **Breakthrough Detection**
   ```sql
   SELECT
     COUNT(*) as breakthroughs,
     AVG(breakthrough_score) as avg_score
   FROM `agi_research_analytics.research_papers`
   WHERE breakthrough_score > 0.8
     AND published_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
   ```

### Set Up Alerts

```bash
# Create alerting policy for high error rate
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05
```

## Troubleshooting

### Common Issues

1. **Service fails to start**
   - Check logs: `gcloud logging read --limit=100`
   - Verify secrets are accessible
   - Check service account permissions

2. **No papers collected**
   - Verify internet connectivity
   - Check API quotas and rate limits
   - Review arxiv.org availability

3. **High API costs**
   - Review number of papers being analyzed
   - Implement result caching
   - Use smaller models where appropriate

4. **Firestore quota exceeded**
   - Increase quota in GCP Console
   - Implement data archival strategy
   - Optimize write operations

## Maintenance

### Regular Tasks

**Weekly:**
- Review error logs
- Check API costs
- Verify data quality

**Monthly:**
- Review and optimize costs
- Update dependencies
- Archive old data
- Review detected breakthroughs

**Quarterly:**
- Major version updates
- Security patches
- Performance optimization
- Model evaluation

### Backup Strategy

Automated backups are configured in Terraform:
- **Firestore**: Daily backups to Cloud Storage
- **BigQuery**: Table snapshots
- **Retention**: 90 days

Manual backup:
```bash
# Export Firestore
gcloud firestore export gs://agi-research-backups/firestore/$(date +%Y%m%d)

# Export BigQuery table
bq extract \
  --destination_format=AVRO \
  agi_research_analytics.research_papers \
  gs://agi-research-backups/bigquery/research_papers_$(date +%Y%m%d).avro
```

## Scaling

### Horizontal Scaling

Services auto-scale based on:
- Request volume
- CPU utilization
- Memory usage

Adjust scaling in Terraform:
```hcl
variable "max_collector_instances" {
  default = 50  # Increase for higher load
}
```

### Vertical Scaling

Increase resources per instance:
```bash
gcloud run services update agi-reasoning-engine \
  --memory=16Gi \
  --cpu=8
```

## Security

### Best Practices

1. **Use Secret Manager** for all credentials
2. **Enable VPC Service Controls** for production
3. **Implement audit logging**
4. **Regular security scans** with Cloud Security Scanner
5. **Principle of least privilege** for service accounts

### Access Control

```bash
# Grant user access to view data
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:email@example.com" \
  --role="roles/bigquery.dataViewer"

# Grant access to API
gcloud run services add-iam-policy-binding agi-api-service \
  --member="user:email@example.com" \
  --role="roles/run.invoker" \
  --region=$REGION
```

## Next Steps

After successful deployment:

1. **Configure alerting** for critical metrics
2. **Set up dashboards** in Cloud Monitoring
3. **Integrate with existing systems** via API
4. **Train team** on using the platform
5. **Establish review process** for detected breakthroughs

## Support

For issues or questions:
- Check logs in Cloud Console
- Review system design document
- Contact: [Your contact information]

---

**Last Updated**: 2025-11-30
**Version**: 1.0
