#!/bin/bash

# Deployment script for Financial Advisor MVP on GCP
# Usage: ./deploy.sh <project-id> <region>

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${1:-"your-project-id"}
REGION=${2:-"europe-west1"}
SERVICE_NAME="financial-advisor-api"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo -e "${GREEN}=== Financial Advisor MVP Deployment ===${NC}"
echo "Project ID: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI not found${NC}"
    echo "Please install: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set project
echo -e "${YELLOW}[1/8] Setting GCP project...${NC}"
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo -e "${YELLOW}[2/8] Enabling required APIs...${NC}"
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    bigquery.googleapis.com \
    storage-api.googleapis.com \
    aiplatform.googleapis.com \
    --project=${PROJECT_ID}

# Create storage bucket
echo -e "${YELLOW}[3/8] Creating Cloud Storage bucket...${NC}"
BUCKET_NAME="${PROJECT_ID}-financial-advisor"
gsutil mb -p ${PROJECT_ID} -l ${REGION} gs://${BUCKET_NAME}/ || echo "Bucket already exists"

# Create BigQuery dataset
echo -e "${YELLOW}[4/8] Creating BigQuery dataset...${NC}"
bq --location=EU mk --dataset ${PROJECT_ID}:financial_data || echo "Dataset already exists"

# Build Docker image
echo -e "${YELLOW}[5/8] Building Docker image...${NC}"
gcloud builds submit --tag ${IMAGE_NAME} --project=${PROJECT_ID}

# Deploy to Cloud Run
echo -e "${YELLOW}[6/8] Deploying to Cloud Run...${NC}"
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --min-instances 0 \
    --max-instances 10 \
    --set-env-vars "GCP_PROJECT_ID=${PROJECT_ID},GOOGLE_API_KEY=$(cat key.txt)" \
    --project=${PROJECT_ID}

# Get service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --platform managed \
    --region ${REGION} \
    --format 'value(status.url)' \
    --project=${PROJECT_ID})

echo -e "${YELLOW}[7/8] Configuring IAM permissions...${NC}"
# Allow Cloud Run to access BigQuery and Storage
SERVICE_ACCOUNT=$(gcloud run services describe ${SERVICE_NAME} \
    --platform managed \
    --region ${REGION} \
    --format 'value(spec.template.spec.serviceAccountName)' \
    --project=${PROJECT_ID})

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/bigquery.dataEditor" \
    --condition=None || true

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/storage.objectAdmin" \
    --condition=None || true

# Upload model to Cloud Storage
echo -e "${YELLOW}[8/8] Uploading model artifacts...${NC}"
if [ -f "models/segmentation_model.pkl" ]; then
    gsutil cp models/segmentation_model.pkl gs://${BUCKET_NAME}/models/
    echo "Model uploaded"
else
    echo "No model found - train model first with: python main.py"
fi

# Summary
echo ""
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo ""
echo "Service URL: ${SERVICE_URL}"
echo "Bucket: gs://${BUCKET_NAME}"
echo "BigQuery Dataset: ${PROJECT_ID}:financial_data"
echo ""
echo "Test the API:"
echo "curl ${SERVICE_URL}/"
echo ""
echo "View logs:"
echo "gcloud run logs read ${SERVICE_NAME} --region ${REGION} --limit 50"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "1. Upload transactions.csv to BigQuery"
echo "2. Train the model: python main.py"
echo "3. Test endpoints: curl ${SERVICE_URL}/api/v1/profile/CUST001"