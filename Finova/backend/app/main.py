from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.db import engine, Base
from app.routes import analysis, health, chat, ml

# Créer les tables
Base.metadata.create_all(bind=engine)

# Initialiser l'app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="API pour l'analyse financière avec chatbot IA Gemini et ML"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router)
app.include_router(analysis.router)
app.include_router(chat.router)
app.include_router(ml.router)


@app.get("/")
async def root():
    """Route racine"""
    return {
        "message": "Bienvenue sur Finova API - Gestion Budgétaire avec IA",
        "version": settings.api_version,
        "docs": "/docs",
        "features": ["Analyse des dépenses", "Chatbot financier", "ML et prédictions", "Dashboards dynamiques"]
    }
