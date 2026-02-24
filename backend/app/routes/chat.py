from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Dict, Any, Optional
import tempfile
import os
from app.services import CSVParser, BudgetChatBot
from app.services.vector_store import VectorStore
from app.database.db import SessionLocal
from app.models.models import Analysis
from pydantic import BaseModel

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Instance globale du VectorStore
vector_store = VectorStore()

# Schema pour les messages chat
class ChatMessage(BaseModel):
    message: str
    analysis_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    context: Optional[Dict[str, Any]] = None
    relevant_expenses: Optional[List[Dict[str, Any]]] = None


@router.post("/message")
async def send_message(chat_msg: ChatMessage):
    """Envoyer un message au chatbot d'analyse financière avec RAG."""
    try:
        chatbot = BudgetChatBot()
        
        # Récupérer le contexte des dépenses si analysis_id fourni
        context = None
        if chat_msg.analysis_id:
            db = SessionLocal()
            analysis = db.query(Analysis).filter(Analysis.id == chat_msg.analysis_id).first()
            if analysis and analysis.expense_data:
                context = chatbot.analyze_expenses(analysis.expense_data)
            db.close()
        
        # Envoyer le message avec RAG activé
        result = chatbot.chat(
            chat_msg.message,
            context=context,
            vector_store=vector_store,
            analysis_id=chat_msg.analysis_id
        )
        
        return ChatResponse(
            response=result['response'],
            context=context,
            relevant_expenses=result.get('relevant_expenses', [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-and-analyze")
async def upload_and_analyze(file: UploadFile = File(...)):
    """Uploader un fichier CSV et recevoir une analyse initiale du chatbot avec RAG."""
    try:
        # Sauvegarder le fichier temporairement
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
        
        # Parser le fichier
        expenses, column_info = CSVParser.parse_file(tmp_path)
        
        # Nettoyer le fichier temporaire
        os.unlink(tmp_path)
        
        # Stocker en BD
        db = SessionLocal()
        analysis = Analysis(
            filename=file.filename,
            expense_data=expenses,
            user_id=1  # TODO: utiliser l'authentification réelle
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        analysis_id = analysis.id
        db.close()
        
        # Ajouter les dépenses au VectorStore pour RAG
        vector_store.add_expenses(expenses, analysis_id)
        
        # Générer une analyse initiale avec le chatbot
        chatbot = BudgetChatBot()
        context = chatbot.analyze_expenses(expenses)
        
        result = chatbot.chat(
            f"Fais un résumé concis de mes dépenses. Je viens d'uploader {len(expenses)} transactions.",
            context=context,
            vector_store=vector_store,
            analysis_id=analysis_id
        )
        
        return {
            "analysis_id": analysis_id,
            "filename": file.filename,
            "expense_count": len(expenses),
            "expenses": expenses,
            "column_mapping": column_info,
            "context": context,
            "initial_analysis": result['response'],
            "rag_enabled": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: int):
    """Récupérer une analyse stockée."""
    db = SessionLocal()
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    db.close()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analyse non trouvée")
    
    chatbot = BudgetChatBot()
    context = chatbot.analyze_expenses(analysis.expense_data)
    
    return {
        "id": analysis.id,
        "filename": analysis.filename,
        "expenses": analysis.expense_data,
        "context": context
    }
