# Finova Backend

Application FastAPI avec agents LangChain pour l'analyse financière.

## Structure

- `app/main.py` - Application FastAPI
- `app/config.py` - Configuration
- `app/agents/` - Agents IA (CFO, Strategist)
- `app/models/` - Models SQLAlchemy et Schemas Pydantic
- `app/routes/` - Routes API
- `app/database/` - Configuration base de données

## Développement Local

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer l'API
uvicorn app.main:app --reload

# Voir la doc
http://localhost:8000/docs
```

## Variables d'Environnement

- `DATABASE_URL` - Connection PostgreSQL
- `GEMINI_API_KEY` - Clé API Google Gemini
- `ENVIRONMENT` - development ou production
