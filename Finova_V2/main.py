"""
Main Pipeline - Financial Advisor MVP
Orchestrates the complete workflow from data to advice
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path

from data_preprocessing import FinancialDataPreprocessor
from clustering_model import CustomerSegmentationModel
from gemini_advisor import GeminiFinancialAdvisor
from gcp_deployment import GCPDeployment

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FinancialAdvisorPipeline:
    """Complete ML pipeline for financial advisor"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize pipeline components"""
        self.preprocessor = FinancialDataPreprocessor()
        self.model = CustomerSegmentationModel(n_clusters=5)
        self.advisor = GeminiFinancialAdvisor()
        
        # Create necessary directories
        Path("models").mkdir(exist_ok=True)
        Path("outputs").mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        
        logger.info("Pipeline initialized")
    
    def run_training_pipeline(self, csv_path: str = "transactions.csv"):
        """
        Complete training pipeline
        
        Steps:
        1. Load and preprocess data
        2. Train clustering model
        3. Save model artifacts
        4. Generate sample predictions
        """
        logger.info("=" * 80)
        logger.info("STARTING TRAINING PIPELINE")
        logger.info("=" * 80)
        
        # Step 1: Preprocess data
        logger.info("\n[1/4] Loading and preprocessing data...")
        features, profile = self.preprocessor.prepare_for_training(csv_path)
        
        logger.info(f"✓ Generated {len(features.columns)} features")
        logger.info(f"✓ Analyzed {len(features)} months of data")
        
        # Step 2: Prepare training data
        logger.info("\n[2/4] Preparing training data...")
        
        # For MVP, create synthetic variations of the profile
        # In production, you'd have multiple real customers
        training_profiles = self._create_training_data(profile, n_samples=100)
        logger.info(f"✓ Created {len(training_profiles)} training samples")
        
        # Step 3: Train model
        logger.info("\n[3/4] Training clustering model...")
        metrics = self.model.train(training_profiles)
        
        logger.info(f"✓ Training complete")
        logger.info(f"  - Silhouette Score: {metrics['silhouette_score']:.3f}")
        logger.info(f"  - Inertia: {metrics['inertia']:.2f}")
        logger.info(f"  - Samples: {metrics['n_samples']}")
        
        # Display cluster profiles
        logger.info("\n  Cluster Profiles:")
        for cluster_id, info in self.model.cluster_profiles.items():
            logger.info(f"    Cluster {cluster_id}: {info['persona']} ({info['size']} customers)")
        
        # Step 4: Save model
        logger.info("\n[4/4] Saving model artifacts...")
        model_path = "models/segmentation_model.pkl"
        self.model.save_model(model_path)
        logger.info(f"✓ Model saved to {model_path}")
        
        # Save metadata
        metadata = {
            'training_date': datetime.now().isoformat(),
            'metrics': metrics,
            'n_features': len(profile),
            'clusters': {
                int(k): {
                    'persona': v['persona'],
                    'size': v['size']
                }
                for k, v in self.model.cluster_profiles.items()
            }
        }
        
        with open("models/model_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info("✓ Metadata saved")
        
        logger.info("\n" + "=" * 80)
        logger.info("TRAINING PIPELINE COMPLETE")
        logger.info("=" * 80)
        
        return metrics
    
    def run_inference_pipeline(
        self,
        csv_path: str = "transactions.csv",
        customer_id: str = "CUST001",
        goal: str = "maximize monthly savings"
    ):
        """
        Complete inference pipeline
        
        Steps:
        1. Load customer data
        2. Predict cluster
        3. Generate personalized advice
        4. Save results
        """
        logger.info("=" * 80)
        logger.info(f"STARTING INFERENCE PIPELINE for {customer_id}")
        logger.info("=" * 80)
        
        # Step 1: Load data
        logger.info("\n[1/4] Loading customer data...")
        features, profile = self.preprocessor.prepare_for_training(csv_path)
        logger.info("✓ Data loaded and processed")
        
        # Step 2: Load model and predict
        logger.info("\n[2/4] Predicting customer segment...")
        try:
            self.model.load_model("models/segmentation_model.pkl")
            cluster_id, cluster_info = self.model.predict(profile)
            
            logger.info(f"✓ Customer classified as: {cluster_info['persona']}")
            logger.info(f"  - Cluster ID: {cluster_id}")
            logger.info(f"  - Cluster Size: {cluster_info['size']} customers")
        except Exception as e:
            logger.error(f"✗ Model prediction failed: {e}")
            logger.info("  Running training pipeline first...")
            self.run_training_pipeline(csv_path)
            cluster_id, cluster_info = self.model.predict(profile)
        
        # Step 3: Generate advice
        logger.info("\n[3/4] Generating personalized advice...")
        advice = self.advisor.generate_advice(profile, cluster_info, goal)
        logger.info("✓ Advice generated")
        
        # Step 4: Save and display results
        logger.info("\n[4/4] Saving results...")
        
        results = {
            'customer_id': customer_id,
            'analysis_date': datetime.now().isoformat(),
            'profile': profile,
            'cluster_id': int(cluster_id),
            'cluster_info': {
                'persona': cluster_info['persona'],
                'size': cluster_info['size']
            },
            'advice': advice,
            'goal': goal
        }
        
        output_file = f"outputs/advice_{customer_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"✓ Results saved to {output_file}")
        
        # Display advice
        self._display_advice(results)
        
        logger.info("\n" + "=" * 80)
        logger.info("INFERENCE PIPELINE COMPLETE")
        logger.info("=" * 80)
        
        return results
    
    def _create_training_data(self, base_profile: dict, n_samples: int = 100):
        """Create synthetic training data by adding noise to base profile"""
        import numpy as np
        
        profiles = []
        
        for _ in range(n_samples):
            noisy_profile = {}
            for key, value in base_profile.items():
                # Add Gaussian noise (5-15% variation)
                noise = np.random.normal(0, abs(value) * 0.1)
                noisy_value = value + noise
                
                # Ensure ratios stay between 0 and 1
                if 'ratio' in key:
                    noisy_value = max(0.0, min(1.0, noisy_value))
                # Ensure positive values for amounts
                elif 'income' in key or 'spending' in key or 'transaction' in key:
                    noisy_value = max(0.0, noisy_value)
                
                noisy_profile[key] = noisy_value
            
            profiles.append(list(noisy_profile.values()))
        
        return profiles
    
    def _display_advice(self, results: dict):
        """Pretty print advice to console"""
        logger.info("\n" + "=" * 80)
        logger.info("PERSONALIZED FINANCIAL ADVICE")
        logger.info("=" * 80)
        
        logger.info(f"\nCustomer ID: {results['customer_id']}")
        logger.info(f"Profile: {results['cluster_info']['persona']}")
        logger.info(f"Goal: {results['goal']}")
        
        for section, content in results['advice'].items():
            logger.info(f"\n{section.upper().replace('_', ' ')}")
            logger.info("-" * 80)
            logger.info(content)
    
    def deploy_to_gcp(
        self,
        project_id: str,
        bucket_name: str = "financial-advisor-mvp"
    ):
        """Deploy model and data to GCP"""
        logger.info("=" * 80)
        logger.info("DEPLOYING TO GCP")
        logger.info("=" * 80)
        
        deployment = GCPDeployment(project_id)
        
        # Step 1: Create dataset
        logger.info("\n[1/4] Creating BigQuery dataset...")
        deployment.create_bigquery_dataset("financial_data")
        
        # Step 2: Upload transactions
        logger.info("\n[2/4] Uploading transaction data...")
        if os.path.exists("transactions.csv"):
            deployment.upload_transactions_to_bigquery(
                "transactions.csv",
                "financial_data",
                "transactions"
            )
        
        # Step 3: Upload model
        logger.info("\n[3/4] Uploading model to Cloud Storage...")
        deployment.upload_to_cloud_storage(
            "models/segmentation_model.pkl",
            bucket_name,
            "models/segmentation_model.pkl"
        )
        
        # Step 4: Deploy to Vertex AI (optional)
        logger.info("\n[4/4] Model ready for Vertex AI deployment")
        logger.info("  (Manual step: Deploy via Vertex AI console)")
        
        logger.info("\n" + "=" * 80)
        logger.info("GCP DEPLOYMENT COMPLETE")
        logger.info("=" * 80)


def main():
    """Main execution"""
    
    # Check if transactions.csv exists
    if not os.path.exists("transactions.csv"):
        logger.error("transactions.csv not found!")
        logger.info("Please place your CSV file in the working directory")
        return
    
    # Initialize pipeline
    pipeline = FinancialAdvisorPipeline()
    
    # Run training pipeline
    logger.info("\nStarting training pipeline...")
    metrics = pipeline.run_training_pipeline("transactions.csv")
    
    # Run inference pipeline
    logger.info("\n\nStarting inference pipeline...")
    results = pipeline.run_inference_pipeline(
        "transactions.csv",
        customer_id="CUST001",
        goal="save €500/month for home down payment"
    )
    
    # Optional: Deploy to GCP
    # Uncomment and set your project ID
    # project_id = os.getenv("GCP_PROJECT_ID")
    # if project_id:
    #     pipeline.deploy_to_gcp(project_id)
    
    logger.info("\n\n✓ ALL PIPELINES COMPLETE ✓")
    logger.info("\nNext steps:")
    logger.info("1. Review the advice in outputs/")
    logger.info("2. Start the API: python api_service.py")
    logger.info("3. Deploy to GCP if needed")


if __name__ == "__main__":
    main()