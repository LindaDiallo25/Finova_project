from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
import json
from typing import List
from app.database.db import get_db
from app.models.models import Analysis, InvestmentScenario
from app.models.schemas import AnalysisResponse, CFOAnalysisResponse, StrategistResponse
from app.agents.cfo_agent import CFOAgent
from app.agents.strategist_agent import StrategistAgent

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

cfo = CFOAgent()
strategist = StrategistAgent()


@router.post("/upload-file")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload et analyse un fichier CSV ou Excel"""
    
    try:
        # Lire le fichier
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file.file)
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file.file)
        else:
            raise HTTPException(status_code=400, detail="Format de fichier non supporté")
        
        # Convertir en liste de dictionnaires
        expense_data = df.to_dict('records')
        
        # Analyser avec l'agent CFO
        cfo_analysis = cfo.analyze_expenses(expense_data)
        
        # Sauvegarder en base de données
        analysis = Analysis(
            user_id=1,  # À remplacer par l'ID utilisateur réel
            filename=file.filename,
            expense_data=expense_data,
            cfo_analysis=json.dumps(cfo_analysis),
            trends=json.dumps(cfo_analysis.get("trends", []))
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        return {
            "analysis_id": analysis.id,
            "filename": file.filename,
            "cfo_analysis": cfo_analysis
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-scenarios/{analysis_id}")
async def generate_scenarios(analysis_id: int, db: Session = Depends(get_db)):
    """Génère des scénarios d'investissement"""
    
    try:
        # Récupérer l'analyse
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analyse non trouvée")
        
        # Parser les données
        cfo_analysis = json.loads(analysis.cfo_analysis)
        
        # Générer les scénarios
        scenarios_data = strategist.generate_scenarios(
            total_expenses=cfo_analysis.get("total_expenses", 0),
            trends=cfo_analysis.get("trends", []),
            recommendations=cfo_analysis.get("recommendations", [])
        )
        
        # Sauvegarder les scénarios
        saved_scenarios = []
        for scenario in scenarios_data.get("scenarios", []):
            investment_scenario = InvestmentScenario(
                analysis_id=analysis_id,
                scenario_number=scenario["scenario_number"],
                title=scenario["title"],
                description=scenario["description"],
                expected_return=scenario["expected_return"],
                risk_level=scenario["risk_level"],
                details=scenario.get("details", {})
            )
            db.add(investment_scenario)
            db.commit()
            db.refresh(investment_scenario)
            saved_scenarios.append(investment_scenario)
        
        return {
            "analysis_id": analysis_id,
            "scenarios": saved_scenarios,
            "market_comparison": scenarios_data.get("market_comparison", {})
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """Récupère une analyse"""
    
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analyse non trouvée")
    
    cfo_analysis = json.loads(analysis.cfo_analysis)
    
    return {
        "id": analysis.id,
        "filename": analysis.filename,
        "cfo_analysis": cfo_analysis,
        "created_at": analysis.created_at
    }


@router.get("/scenarios/{analysis_id}")
async def get_scenarios(analysis_id: int, db: Session = Depends(get_db)):
    """Récupère les scénarios d'une analyse"""
    
    scenarios = db.query(InvestmentScenario).filter(
        InvestmentScenario.analysis_id == analysis_id
    ).all()
    
    return scenarios
