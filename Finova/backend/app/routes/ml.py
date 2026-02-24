from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.services.ml_engine import MLEngine
from app.database.db import SessionLocal
from app.models.models import Analysis

router = APIRouter(prefix="/api/ml", tags=["ml"])


class ExpenseData(BaseModel):
    expenses: List[Dict[str, Any]]


class PredictionRequest(BaseModel):
    analysis_id: int
    days_ahead: int = 30
    by_category: bool = True


class AnomalyRequest(BaseModel):
    analysis_id: int
    contamination: float = 0.1


@router.post("/anomalies")
async def detect_anomalies(request: AnomalyRequest):
    """
    Détecte les transactions anormales dans une analyse
    
    Query params:
    - analysis_id: ID de l'analyse
    - contamination: Proportion d'anomalies attendues (défaut: 0.1)
    
    Returns:
    - anomalies: Liste des transactions anormales avec scores de sévérité
    """
    try:
        db = SessionLocal()
        analysis = db.query(Analysis).filter(Analysis.id == request.analysis_id).first()
        
        if not analysis or not analysis.expense_data:
            raise HTTPException(status_code=404, detail="Analyse non trouvée")
        
        expenses = analysis.expense_data if isinstance(analysis.expense_data, list) else []
        
        result = MLEngine.detect_anomalies(expenses, contamination=request.contamination)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur ML: {str(e)}")


@router.post("/predict")
async def predict_expenses(request: PredictionRequest):
    """
    Prédit les dépenses futures par catégorie
    
    Query params:
    - analysis_id: ID de l'analyse
    - days_ahead: Nombre de jours à prédire (défaut: 30)
    - by_category: Prédire par catégorie? (défaut: true)
    
    Returns:
    - predictions: Dict du format {category: [predictions]}
    """
    try:
        db = SessionLocal()
        analysis = db.query(Analysis).filter(Analysis.id == request.analysis_id).first()
        
        if not analysis or not analysis.expense_data:
            raise HTTPException(status_code=404, detail="Analyse non trouvée")
        
        expenses = analysis.expense_data if isinstance(analysis.expense_data, list) else []
        
        result = MLEngine.predict_expenses(
            expenses,
            days_ahead=request.days_ahead,
            by_category=request.by_category
        )
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur ML: {str(e)}")


@router.post("/budget-recommendations")
async def get_budget_recommendations(analysis_id: int, percentile: float = 75):
    """
    Recommande un budget optimal par catégorie
    
    Query params:
    - analysis_id: ID de l'analyse
    - percentile: Percentile pour les recommandations (défaut: 75)
    
    Returns:
    - recommendations: Budget recommandé par catégorie
    """
    try:
        db = SessionLocal()
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        
        if not analysis or not analysis.expense_data:
            raise HTTPException(status_code=404, detail="Analyse non trouvée")
        
        expenses = analysis.expense_data if isinstance(analysis.expense_data, list) else []
        
        result = MLEngine.get_budget_recommendations(expenses, percentile=percentile)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur ML: {str(e)}")


@router.post("/patterns")
async def analyze_spending_patterns(analysis_id: int):
    """
    Analyse les patterns de dépenses
    
    Query params:
    - analysis_id: ID de l'analyse
    
    Returns:
    - patterns: Insights sur les tendances, volatilité, etc.
    """
    try:
        db = SessionLocal()
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        
        if not analysis or not analysis.expense_data:
            raise HTTPException(status_code=404, detail="Analyse non trouvée")
        
        expenses = analysis.expense_data if isinstance(analysis.expense_data, list) else []
        
        result = MLEngine.analyze_spending_patterns(expenses)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur ML: {str(e)}")


@router.get("/health")
async def ml_health():
    """Vérifie que le service ML est fonctionnel"""
    return {
        "status": "ok",
        "ml_service": "active",
        "available_models": [
            "anomaly_detection",
            "expense_prediction",
            "budget_recommendations",
            "pattern_analysis"
        ]
    }
