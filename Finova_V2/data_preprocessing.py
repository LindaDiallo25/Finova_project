"""
Data Preprocessing Pipeline for Financial Advisor MVP
Transforms transaction data into features for ML model
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FinancialDataPreprocessor:
    """Preprocessor for banking transaction data"""
    
    def __init__(self):
        self.category_mappings = {
            'Groceries': 'Essential',
            'Utilities': 'Essential',
            'Gas & Fuel': 'Essential',
            'Restaurants': 'Discretionary',
            'Shopping': 'Discretionary',
            'Entertainment': 'Discretionary',
            'Movies & DVDs': 'Discretionary',
            'Coffee Shops': 'Discretionary',
            'Fast Food': 'Discretionary',
            'Alcohol & Bars': 'Discretionary',
            'Mortgage & Rent': 'Fixed',
            'Mobile Phone': 'Fixed',
            'Internet': 'Fixed',
            'Auto Insurance': 'Fixed',
            'Haircut': 'Discretionary',
            'Home Improvement': 'Investment'
        }
    
    def load_data(self, csv_path: str) -> pd.DataFrame:
        """Load transaction data from CSV"""
        logger.info(f"Loading data from {csv_path}")
        df = pd.read_csv(csv_path)
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create features from transaction data"""
        logger.info("Engineering features...")
        
        # Separate credits and debits
        debits = df[df['TransactionType'] == 'debit'].copy()
        credits = df[df['TransactionType'] == 'credit'].copy()
        
        # Monthly aggregations
        debits['YearMonth'] = debits['Date'].dt.to_period('M')
        credits['YearMonth'] = credits['Date'].dt.to_period('M')
        
        # Calculate monthly income
        monthly_income = credits.groupby('YearMonth')['Amount'].sum()
        
        # Calculate spending by category
        debits['CategoryType'] = debits['Category'].map(
            lambda x: self.category_mappings.get(x, 'Other')
        )
        
        monthly_spending = debits.groupby(['YearMonth', 'CategoryType'])['Amount'].sum().unstack(fill_value=0)
        
        # Calculate key metrics
        features = pd.DataFrame()
        features['monthly_income'] = monthly_income
        features['total_spending'] = debits.groupby('YearMonth')['Amount'].sum()
        features['savings_rate'] = (features['monthly_income'] - features['total_spending']) / features['monthly_income']
        
        # Spending ratios
        for cat in ['Essential', 'Discretionary', 'Fixed', 'Investment']:
            if cat in monthly_spending.columns:
                features[f'{cat.lower()}_spending'] = monthly_spending[cat]
                features[f'{cat.lower()}_ratio'] = monthly_spending[cat] / features['total_spending']
            else:
                features[f'{cat.lower()}_spending'] = 0
                features[f'{cat.lower()}_ratio'] = 0
        
        # Transaction behavior
        features['transaction_count'] = debits.groupby('YearMonth').size()
        features['avg_transaction_size'] = features['total_spending'] / features['transaction_count']
        
        # Spending volatility (std dev of daily spending)
        daily_spending = debits.groupby([debits['Date'].dt.to_period('M'), 'Date'])['Amount'].sum()
        features['spending_volatility'] = daily_spending.groupby(level=0).std()
        
        # Fill NaN values
        features = features.fillna(0)
        
        logger.info(f"Generated {len(features.columns)} features for {len(features)} months")
        return features
    
    def create_customer_profile(self, features: pd.DataFrame) -> Dict:
        """Aggregate features into single customer profile"""
        logger.info("Creating customer profile...")
        
        profile = {
            'avg_monthly_income': features['monthly_income'].mean(),
            'avg_monthly_spending': features['total_spending'].mean(),
            'avg_savings_rate': features['savings_rate'].mean(),
            'essential_ratio': features['essential_ratio'].mean(),
            'discretionary_ratio': features['discretionary_ratio'].mean(),
            'fixed_ratio': features['fixed_ratio'].mean(),
            'investment_ratio': features['investment_ratio'].mean(),
            'avg_transaction_count': features['transaction_count'].mean(),
            'avg_transaction_size': features['avg_transaction_size'].mean(),
            'spending_volatility': features['spending_volatility'].mean(),
            'income_trend': self._calculate_trend(features['monthly_income']),
            'spending_trend': self._calculate_trend(features['total_spending']),
        }
        
        return profile
    
    def _calculate_trend(self, series: pd.Series) -> float:
        """Calculate linear trend coefficient"""
        if len(series) < 2:
            return 0.0
        x = np.arange(len(series))
        y = series.values
        if np.std(y) == 0:
            return 0.0
        return np.corrcoef(x, y)[0, 1]
    
    def prepare_for_training(self, csv_path: str) -> Tuple[pd.DataFrame, Dict]:
        """Complete preprocessing pipeline"""
        df = self.load_data(csv_path)
        features = self.engineer_features(df)
        profile = self.create_customer_profile(features)
        
        return features, profile


if __name__ == "__main__":
    preprocessor = FinancialDataPreprocessor()
    features, profile = preprocessor.prepare_for_training("transactions.csv")
    
    print("\n=== Customer Profile ===")
    for key, value in profile.items():
        print(f"{key}: {value:.2f}")
    
    print("\n=== Monthly Features (last 5 months) ===")
    print(features.tail())