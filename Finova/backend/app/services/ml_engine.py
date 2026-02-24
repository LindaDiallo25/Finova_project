import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
from prophet import Prophet
import warnings
import json

warnings.filterwarnings('ignore')


class MLEngine:
    """Service de Machine Learning pour anályse de dépenses avec prédictions et détection d'anomalies"""

    @staticmethod
    def _safe_float(value):
        """Convertit une valeur en float sûr pour JSON (remplace inf/nan par 0)"""
        try:
            f = float(value)
            if np.isnan(f) or np.isinf(f):
                return 0.0
            return f
        except:
            return 0.0

    @staticmethod
    def detect_anomalies(expenses: List[Dict[str, Any]], contamination: float = 0.1) -> Dict[str, Any]:
        """
        Détecte les transactions anormales using Isolation Forest
        
        Args:
            expenses: Liste des dépenses avec structure {category, amount, date, description}
            contamination: Proportion d'anomalies attendues (0.1 = 10%)
        
        Returns:
            Dict avec anomalies détectées et score de sévérité
        """
        if not expenses or len(expenses) < 5:
            return {"anomalies": [], "message": "Données insuffisantes pour l'analyse"}

        try:
            df = pd.DataFrame(expenses)
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            df = df.dropna(subset=['amount'])

            # Features pour Isolation Forest
            features = df[['amount']].copy()
            
            # Ajouter statistiques par catégorie
            category_mean = df.groupby('category')['amount'].transform('mean')
            category_std = df.groupby('category')['amount'].transform('std').fillna(1)
            
            features['z_score'] = np.abs((df['amount'] - category_mean) / category_std)
            features['category_deviation'] = np.abs(df['amount'] - category_mean) / (category_mean + 1)
            
            # Remplir les NaN avec 0
            features = features.fillna(0)

            # Ajuster contamination selon le nombre d'entrées
            actual_contamination = min(contamination, 1.0 / len(features)) if len(features) > 10 else 0.05
            
            # Isolation Forest
            iso_forest = IsolationForest(
                contamination=actual_contamination,
                random_state=42,
                n_estimators=100
            )
            predictions = iso_forest.fit_predict(features)
            scores = iso_forest.score_samples(features)

            # Combiner les résultats
            df['anomaly'] = predictions == -1
            
            # Calculer la sévérité avec protection contre la division par zéro
            score_range = scores.max() - scores.min()
            df['severity'] = 1 - ((scores - scores.min()) / score_range) if score_range != 0 else 0.5
            
            anomalies = df[df['anomaly']].copy()
            anomalies = anomalies.sort_values('severity', ascending=False)

            # Formater les résultats
            result_anomalies = []
            for _, row in anomalies.iterrows():
                category_avg = df[df['category'] == row['category']]['amount'].mean()
                deviation = ((row['amount'] - category_avg) / category_avg * 100) if category_avg > 0 else 0
                
                result_anomalies.append({
                    "date": str(row['date']),
                    "category": row['category'],
                    "amount": float(row['amount']),
                    "description": row.get('description', 'N/A'),
                    "severity": float(row['severity']),
                    "category_average": float(category_avg),
                    "deviation_percent": float(deviation),
                    "reason": f"Déviation de {abs(deviation):.1f}% par rapport à la moyenne de la catégorie"
                })

            return {
                "anomalies": result_anomalies,
                "anomaly_count": len(result_anomalies),
                "total_transactions": len(df),
                "anomaly_percentage": (len(result_anomalies) / len(df) * 100) if len(df) > 0 else 0
            }

        except Exception as e:
            return {"anomalies": [], "error": str(e)}

    @staticmethod
    def predict_expenses(expenses: List[Dict[str, Any]], days_ahead: int = 30, by_category: bool = True) -> Dict[str, Any]:
        """
        Prédit les dépenses futures avec Prophet ou moyennes simples
        
        Args:
            expenses: Liste des dépenses
            days_ahead: Nombre de jours à prédire (par défaut 30)
            by_category: Si True, prédit par catégorie; sinon, total global
        
        Returns:
            Dict avec prédictions et intervalles de confiance
        """
        if not expenses or len(expenses) < 5:
            return {"predictions": [], "message": "Au minimum 5 transactions requises"}

        try:
            df = pd.DataFrame(expenses)
            df['date'] = pd.to_datetime(df['date'])
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            df = df.dropna(subset=['amount', 'date'])

            predictions_result = {}

            if by_category:
                # Prédiction par catégorie
                categories = df['category'].unique()
                
                for category in categories:
                    cat_data = df[df['category'] == category].copy()
                    
                    if len(cat_data) < 2:
                        continue

                    # Agréger par jour
                    daily_cat = cat_data.groupby('date')['amount'].sum().reset_index()
                    daily_cat.columns = ['ds', 'y']
                    daily_cat = daily_cat.sort_values('ds')

                    # Utiliser Prophet si on a assez de points, sinon utiliser moyennes
                    if len(daily_cat) >= 5:
                        try:
                            # Prophet avec interval de confiance
                            model = Prophet(
                                interval_width=0.80,
                                yearly_seasonality=False,
                                weekly_seasonality=len(daily_cat) > 14,
                                daily_seasonality=False,
                                changepoint_prior_scale=0.05
                            )
                            model.fit(daily_cat)

                            # Créer future dataframe
                            future = model.make_future_dataframe(periods=days_ahead)
                            forecast = model.predict(future)

                            # Récupérer les derniers jours prédits
                            forecast_future = forecast.tail(days_ahead)[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

                            predictions_result[category] = [
                                {
                                    "date": str(row['ds'].date()),
                                    "predicted_amount": float(max(0, row['yhat'])),  # Pas de montants négatifs
                                    "lower_bound": float(max(0, row['yhat_lower'])),
                                    "upper_bound": float(max(0, row['yhat_upper']))
                                }
                                for _, row in forecast_future.iterrows()
                            ]
                        except Exception as e:
                            # Fallback à moyennes simples si Prophet échoue
                            avg_amount = daily_cat['y'].mean()
                            std_amount = daily_cat['y'].std()
                            
                            predictions_result[category] = [
                                {
                                    "date": (df['date'].max() + timedelta(days=i+1)).strftime('%Y-%m-%d'),
                                    "predicted_amount": float(max(0, avg_amount)),
                                    "lower_bound": float(max(0, avg_amount - std_amount)),
                                    "upper_bound": float(max(0, avg_amount + std_amount))
                                }
                                for i in range(days_ahead)
                            ]
                    else:
                        # Prédictions simples basées sur moyenne/std
                        avg_amount = daily_cat['y'].mean()
                        std_amount = daily_cat['y'].std() if len(daily_cat) > 1 else 0
                        
                        predictions_result[category] = [
                            {
                                "date": (df['date'].max() + timedelta(days=i+1)).strftime('%Y-%m-%d'),
                                "predicted_amount": float(max(0, avg_amount)),
                                "lower_bound": float(max(0, avg_amount - std_amount)),
                                "upper_bound": float(max(0, avg_amount + std_amount))
                            }
                            for i in range(days_ahead)
                        ]

            else:
                # Prédiction globale par jour
                daily_total = df.groupby('date')['amount'].sum().reset_index()
                daily_total.columns = ['ds', 'y']
                daily_total = daily_total.sort_values('ds')

                if len(daily_total) >= 5:
                    try:
                        model = Prophet(
                            interval_width=0.80,
                            yearly_seasonality=False,
                            weekly_seasonality=len(daily_total) > 14,
                            daily_seasonality=False
                        )
                        model.fit(daily_total)

                        future = model.make_future_dataframe(periods=days_ahead)
                        forecast = model.predict(future)

                        forecast_future = forecast.tail(days_ahead)[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

                        predictions_result["total"] = [
                            {
                                "date": str(row['ds'].date()),
                                "predicted_amount": float(max(0, row['yhat'])),
                                "lower_bound": float(max(0, row['yhat_lower'])),
                                "upper_bound": float(max(0, row['yhat_upper']))
                            }
                            for _, row in forecast_future.iterrows()
                        ]
                    except Exception as e:
                        # Fallback
                        avg_amount = daily_total['y'].mean()
                        std_amount = daily_total['y'].std()
                        
                        predictions_result["total"] = [
                            {
                                "date": (df['date'].max() + timedelta(days=i+1)).strftime('%Y-%m-%d'),
                                "predicted_amount": float(max(0, avg_amount)),
                                "lower_bound": float(max(0, avg_amount - std_amount)),
                                "upper_bound": float(max(0, avg_amount + std_amount))
                            }
                            for i in range(days_ahead)
                        ]
                else:
                    avg_amount = daily_total['y'].mean()
                    std_amount = daily_total['y'].std() if len(daily_total) > 1 else 0
                    
                    predictions_result["total"] = [
                        {
                            "date": (df['date'].max() + timedelta(days=i+1)).strftime('%Y-%m-%d'),
                            "predicted_amount": float(max(0, avg_amount)),
                            "lower_bound": float(max(0, avg_amount - std_amount)),
                            "upper_bound": float(max(0, avg_amount + std_amount))
                        }
                        for i in range(days_ahead)
                    ]

            # Calculer stats
            total_predictions = sum(len(v) if isinstance(v, list) else 0 for v in predictions_result.values())

            return {
                "predictions": predictions_result,
                "prediction_period_days": days_ahead,
                "total_prediction_points": total_predictions,
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {"predictions": [], "error": str(e)}

    @staticmethod
    def get_budget_recommendations(expenses: List[Dict[str, Any]], percentile: float = 75) -> Dict[str, Any]:
        """
        Recommande un budget optimal par catégorie basé sur percentiles historiques
        
        Args:
            expenses: Liste des dépenses
            percentile: Percentile pour les recommandations (75 = 75e percentile)
        
        Returns:
            Dict avec recommandations de budget par catégorie
        """
        if not expenses:
            return {"recommendations": {}, "message": "Aucune donnée disponible"}

        try:
            df = pd.DataFrame(expenses)
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            df = df.dropna(subset=['amount'])

            recommendations = {}

            for category in df['category'].unique():
                cat_amounts = df[df['category'] == category]['amount']
                
                recommendations[category] = {
                    "recommended_budget": float(np.percentile(cat_amounts, percentile)),
                    "average_spent": float(cat_amounts.mean()),
                    "min_spent": float(cat_amounts.min()),
                    "max_spent": float(cat_amounts.max()),
                    "total_transactions": len(cat_amounts),
                    "based_on_percentile": percentile
                }

            # Recommandation globale
            total_spent = df['amount'].sum()
            return {
                "recommendations": recommendations,
                "total_budget_recommended": float(np.percentile(df['amount'].sum(), percentile)),
                "total_spent": float(total_spent),
                "average_transaction": float(df['amount'].mean()),
                "analysis_date": datetime.now().isoformat()
            }

        except Exception as e:
            return {"recommendations": {}, "error": str(e)}

    @staticmethod
    def analyze_spending_patterns(expenses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyse les patterns de dépenses (tendances, volatilité, etc.)
        
        Args:
            expenses: Liste des dépenses
        
        Returns:
            Dict avec insights sur les patterns
        """
        if not expenses or len(expenses) < 5:
            return {"patterns": {}, "message": "Données insuffisantes"}

        try:
            df = pd.DataFrame(expenses)
            df['date'] = pd.to_datetime(df['date'])
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            df = df.dropna(subset=['amount', 'date'])

            patterns = {}

            # 1. Tendance générale
            daily_totals = df.groupby('date')['amount'].sum().sort_index()
            if len(daily_totals) > 1:
                trend = (daily_totals.iloc[-1] - daily_totals.iloc[0]) / daily_totals.iloc[0] * 100 if daily_totals.iloc[0] > 0 else 0
                patterns["spending_trend"] = {
                    "direction": "croissante" if trend > 0 else "décroissante",
                    "percentage_change": MLEngine._safe_float(trend)
                }

            # 2. Volatilité par catégorie
            category_volatility = {}
            for category in df['category'].unique():
                cat_amounts = df[df['category'] == category]['amount']
                volatility = cat_amounts.std() / cat_amounts.mean() if cat_amounts.mean() > 0 else 0
                category_volatility[category] = MLEngine._safe_float(volatility)

            patterns["category_volatility"] = category_volatility

            # 3. Top catégories
            top_categories = df.groupby('category')['amount'].sum().nlargest(5)
            patterns["top_categories"] = [
                {"category": cat, "total": MLEngine._safe_float(amount)}
                for cat, amount in top_categories.items()
            ]

            # 4. Jour avec max de dépenses
            max_day = daily_totals.idxmax()
            patterns["highest_spending_day"] = {
                "date": str(max_day.date()),
                "amount": MLEngine._safe_float(daily_totals.max())
            }

            return {
                "patterns": patterns,
                "data_points": len(df),
                "date_range": {
                    "start": str(df['date'].min().date()),
                    "end": str(df['date'].max().date())
                }
            }

        except Exception as e:
            return {"patterns": {}, "error": str(e)}
