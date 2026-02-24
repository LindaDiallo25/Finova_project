"""
Customer Segmentation Model using K-Means Clustering
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import joblib
import logging
from typing import Dict, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomerSegmentationModel:
    """K-Means clustering model for customer segmentation"""
    
    def __init__(self, n_clusters: int = 5, random_state: int = 42):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.model = None
        self.feature_names = None
        self.cluster_profiles = None
        
    def prepare_features(self, profile: Dict) -> np.ndarray:
        """Convert profile dict to feature array"""
        feature_order = [
            'avg_monthly_income',
            'avg_monthly_spending',
            'avg_savings_rate',
            'essential_ratio',
            'discretionary_ratio',
            'fixed_ratio',
            'investment_ratio',
            'avg_transaction_count',
            'avg_transaction_size',
            'spending_volatility',
            'income_trend',
            'spending_trend'
        ]
        
        self.feature_names = feature_order
        features = np.array([profile[key] for key in feature_order]).reshape(1, -1)
        return features
    
    def train(self, features_list: list) -> Dict:
        """Train clustering model on multiple customer profiles"""
        logger.info(f"Training K-Means with {self.n_clusters} clusters...")
        
        # Convert to array
        X = np.array(features_list)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train K-Means
        self.model = KMeans(
            n_clusters=self.n_clusters,
            random_state=self.random_state,
            n_init=10,
            max_iter=300
        )
        
        labels = self.model.fit_predict(X_scaled)
        
        # Calculate metrics
        # silhouette = silhouette_score(X_scaled, labels)
        inertia = self.model.inertia_
        
        # Create cluster profiles
        self._create_cluster_profiles(X, labels)
        
        metrics = {
            'silhouette_score': silhouette,
            'inertia': inertia,
            'n_samples': len(X)
        }
        
        logger.info(f"Training complete. Silhouette Score: {silhouette:.3f}")
        return metrics
    
    def _create_cluster_profiles(self, X: np.ndarray, labels: np.ndarray):
        """Create interpretable profiles for each cluster"""
        self.cluster_profiles = {}
        
        for cluster_id in range(self.n_clusters):
            mask = labels == cluster_id
            cluster_data = X[mask]
            
            profile = {}
            for i, feature_name in enumerate(self.feature_names):
                profile[feature_name] = {
                    'mean': float(cluster_data[:, i].mean()),
                    'std': float(cluster_data[:, i].std()),
                    'min': float(cluster_data[:, i].min()),
                    'max': float(cluster_data[:, i].max())
                }
            
            # Assign persona
            persona = self._assign_persona(profile)
            profile['persona'] = persona
            profile['size'] = int(mask.sum())
            
            self.cluster_profiles[int(cluster_id)] = profile
    
    def _assign_persona(self, profile: Dict) -> str:
        """Assign persona based on cluster characteristics"""
        savings_rate = profile['avg_savings_rate']['mean']
        discretionary = profile['discretionary_ratio']['mean']
        income = profile['avg_monthly_income']['mean']
        
        if savings_rate > 0.3:
            return "Super Saver"
        elif savings_rate > 0.15 and discretionary < 0.3:
            return "Prudent Planner"
        elif income > 3000 and discretionary > 0.4:
            return "High Earner Spender"
        elif discretionary > 0.5:
            return "Lifestyle Enthusiast"
        else:
            return "Budget Conscious"
    
    def predict(self, profile: Dict) -> Tuple[int, Dict]:
        """Predict cluster for new customer profile"""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        features = self.prepare_features(profile)
        features_scaled = self.scaler.transform(features)
        
        cluster_id = int(self.model.predict(features_scaled)[0])
        cluster_info = self.cluster_profiles[cluster_id]
        
        return cluster_id, cluster_info
    
    def save_model(self, path: str = "models/segmentation_model.pkl"):
        """Save model to disk"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'cluster_profiles': self.cluster_profiles,
            'n_clusters': self.n_clusters
        }
        joblib.dump(model_data, path)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str = "models/segmentation_model.pkl"):
        """Load model from disk"""
        model_data = joblib.load(path)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.cluster_profiles = model_data['cluster_profiles']
        self.n_clusters = model_data['n_clusters']
        logger.info(f"Model loaded from {path}")


if __name__ == "__main__":
    # Example usage
    from data_preprocessing import FinancialDataPreprocessor
    
    preprocessor = FinancialDataPreprocessor()
    features, profile = preprocessor.prepare_for_training("transactions.csv")
    
    # Train model
    model = CustomerSegmentationModel(n_clusters=2)
    
    # For demonstration, create synthetic profiles
    # In production, you'd have multiple customers
    profiles = [profile for _ in range(100)]  # Simulate 100 customers
    features_list = [list(p.values()) for p in profiles]
    
    metrics = model.train(features_list)
    print(f"\nTraining Metrics: {metrics}")
    
    # Predict
    cluster_id, cluster_info = model.predict(profile)
    print(f"\nCustomer assigned to Cluster {cluster_id}: {cluster_info['persona']}")
    
    # Save model
    model.save_model()