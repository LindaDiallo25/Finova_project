"""
GCP Deployment utilities for Financial Advisor MVP
Handles BigQuery, Cloud Storage, and Vertex AI operations
"""

from google.cloud import bigquery, storage, aiplatform
import pandas as pd
import json
import logging
from typing import Dict, List
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GCPDeployment:
    """Handle GCP services deployment and integration"""
    
    def __init__(self, project_id: str, region: str = "europe-west1"):
        self.project_id = project_id
        self.region = region
        
        # Initialize clients
        self.bq_client = bigquery.Client(project=project_id)
        self.storage_client = storage.Client(project=project_id)
        
        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=region)
        
        logger.info(f"Initialized GCP clients for project {project_id}")
    
    def create_bigquery_dataset(self, dataset_id: str):
        """Create BigQuery dataset"""
        dataset_ref = f"{self.project_id}.{dataset_id}"
        
        try:
            self.bq_client.get_dataset(dataset_ref)
            logger.info(f"Dataset {dataset_id} already exists")
        except Exception:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "EU"
            dataset = self.bq_client.create_dataset(dataset)
            logger.info(f"Created dataset {dataset_id}")
    
    def upload_transactions_to_bigquery(
        self,
        csv_path: str,
        dataset_id: str,
        table_id: str
    ):
        """Upload transaction data to BigQuery"""
        table_ref = f"{self.project_id}.{dataset_id}.{table_id}"
        
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            autodetect=True,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
        )
        
        with open(csv_path, "rb") as source_file:
            job = self.bq_client.load_table_from_file(
                source_file,
                table_ref,
                job_config=job_config
            )
        
        job.result()
        logger.info(f"Uploaded {csv_path} to {table_ref}")
        
        # Verify
        table = self.bq_client.get_table(table_ref)
        logger.info(f"Table has {table.num_rows} rows")
    
    def query_transactions(self, dataset_id: str, table_id: str) -> pd.DataFrame:
        """Query transaction data from BigQuery"""
        query = f"""
        SELECT *
        FROM `{self.project_id}.{dataset_id}.{table_id}`
        ORDER BY Date DESC
        """
        
        df = self.bq_client.query(query).to_dataframe()
        logger.info(f"Retrieved {len(df)} transactions")
        return df
    
    def upload_to_cloud_storage(
        self,
        local_path: str,
        bucket_name: str,
        blob_name: str
    ):
        """Upload file to Cloud Storage"""
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        blob.upload_from_filename(local_path)
        logger.info(f"Uploaded {local_path} to gs://{bucket_name}/{blob_name}")
    
    def download_from_cloud_storage(
        self,
        bucket_name: str,
        blob_name: str,
        local_path: str
    ):
        """Download file from Cloud Storage"""
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        blob.download_to_filename(local_path)
        logger.info(f"Downloaded gs://{bucket_name}/{blob_name} to {local_path}")
    
    def deploy_model_to_vertex(
        self,
        model_path: str,
        display_name: str,
        serving_container_image: str = "europe-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-0:latest"
    ):
        """Deploy model to Vertex AI"""
        
        # Upload model to Cloud Storage first
        bucket_name = f"{self.project_id}-models"
        blob_name = f"models/{display_name}/model.pkl"
        
        self.upload_to_cloud_storage(model_path, bucket_name, blob_name)
        model_uri = f"gs://{bucket_name}/{blob_name}"
        
        # Upload model to Vertex AI
        model = aiplatform.Model.upload(
            display_name=display_name,
            artifact_uri=model_uri,
            serving_container_image_uri=serving_container_image
        )
        
        logger.info(f"Model uploaded to Vertex AI: {model.resource_name}")
        
        # Deploy to endpoint
        endpoint = model.deploy(
            deployed_model_display_name=display_name,
            machine_type="n1-standard-2",
            min_replica_count=1,
            max_replica_count=3
        )
        
        logger.info(f"Model deployed to endpoint: {endpoint.resource_name}")
        return endpoint
    
    def create_feature_store(self, feature_store_id: str):
        """Create Vertex AI Feature Store"""
        try:
            feature_store = aiplatform.Featurestore.create(
                featurestore_id=feature_store_id,
                online_store_fixed_node_count=1,
            )
            logger.info(f"Created feature store: {feature_store.resource_name}")
            return feature_store
        except Exception as e:
            logger.warning(f"Feature store creation failed: {e}")
            return None
    
    def save_customer_profile(
        self,
        profile: Dict,
        customer_id: str,
        dataset_id: str = "financial_data",
        table_id: str = "customer_profiles"
    ):
        """Save customer profile to BigQuery"""
        table_ref = f"{self.project_id}.{dataset_id}.{table_id}"
        
        # Add metadata
        profile['customer_id'] = customer_id
        profile['updated_at'] = pd.Timestamp.now()
        
        # Convert to DataFrame
        df = pd.DataFrame([profile])
        
        # Upload to BigQuery
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        )
        
        job = self.bq_client.load_table_from_dataframe(
            df, table_ref, job_config=job_config
        )
        job.result()
        
        logger.info(f"Saved profile for customer {customer_id}")
    
    def get_customer_profile(
        self,
        customer_id: str,
        dataset_id: str = "financial_data",
        table_id: str = "customer_profiles"
    ) -> Dict:
        """Retrieve customer profile from BigQuery"""
        query = f"""
        SELECT *
        FROM `{self.project_id}.{dataset_id}.{table_id}`
        WHERE customer_id = '{customer_id}'
        ORDER BY updated_at DESC
        LIMIT 1
        """
        
        df = self.bq_client.query(query).to_dataframe()
        
        if len(df) == 0:
            return None
        
        profile = df.iloc[0].to_dict()
        logger.info(f"Retrieved profile for customer {customer_id}")
        return profile


class VertexAIMonitoring:
    """Monitor deployed models on Vertex AI"""
    
    def __init__(self, project_id: str, region: str = "europe-west1"):
        self.project_id = project_id
        self.region = region
        aiplatform.init(project=project_id, location=region)
    
    def log_prediction(
        self,
        endpoint_id: str,
        features: Dict,
        prediction: Dict
    ):
        """Log prediction for monitoring"""
        # In production, this would write to Cloud Logging
        logger.info(f"Prediction logged for endpoint {endpoint_id}")
        logger.info(f"Features: {features}")
        logger.info(f"Prediction: {prediction}")
    
    def get_model_metrics(self, model_id: str) -> Dict:
        """Get model performance metrics"""
        # In production, this would query from Vertex AI Monitoring
        metrics = {
            'predictions_count': 1000,
            'average_latency_ms': 45,
            'error_rate': 0.01
        }
        return metrics


if __name__ == "__main__":
    # Example usage
    PROJECT_ID = os.getenv("GCP_PROJECT_ID", "your-project-id")
    
    deployment = GCPDeployment(PROJECT_ID)
    
    # Create dataset
    deployment.create_bigquery_dataset("financial_data")
    
    # Upload transactions
    if os.path.exists("transactions.csv"):
        deployment.upload_transactions_to_bigquery(
            "transactions.csv",
            "financial_data",
            "transactions"
        )
    
    print("\nGCP deployment setup complete!")