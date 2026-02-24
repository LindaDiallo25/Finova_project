# Architecture Finova

## Vue d'ensemble

Finova est une architecture microservices complète avec trois couches:

```
┌─────────────────────────────────────────┐
│           Frontend (React)               │
│  - Dark Mode UI (Tailwind + Shadcn)     │
│  - Upload drag-and-drop                 │
│  - Graphiques (Recharts)                │
│  - Routing (React Router)               │
└──────────────┬──────────────────────────┘
               │ HTTP / REST
┌──────────────▼──────────────────────────┐
│        Backend (FastAPI)                │
│  - Agents LangChain (CFO, Strategist)   │
│  - Gemini 2.5 Flash LLM                 │
│  - Upload CSV/Excel parsing             │
│  - API REST avec Swagger                │
└──────────────┬──────────────────────────┘
               │ SQL
┌──────────────▼──────────────────────────┐
│    Database (PostgreSQL)                │
│  - Users, Analyses, Scenarios           │
└─────────────────────────────────────────┘
```

## Flux de Données

### 1. Upload de Fichier
```
[Frontend] 
  ↓ FormData (fichier)
[Backend] 
  ↓ Lire fichier (pandas)
[CFO Agent]
  ↓ Analyser avec Gemini
[Database]
  ↓ Stocker l'analyse
[Frontend]
  ↓ Afficher résultats
```

### 2. Génération de Scénarios
```
[Analysis ID] 
  ↓ Récupérer l'analyse
[Strategist Agent]
  ↓ Générer 3 scénarios avec Gemini
[Database]
  ↓ Stocker les scénarios
[Frontend]
  ↓ Afficher les scénarios + graphiques
```

## Composants Principaux

### Frontend

#### Components
- **FileUploader**: Upload drag-and-drop
- **ExpenseChart**: Graphiques Recharts
- **AnalysisResults**: Résultats CFO
- **InvestmentScenarios**: Scénarios Strategist
- **LoadingSpinner**: Indicateur de chargement

#### Hooks
- **useDropZone**: Gestion du drag-and-drop
- **useApi**: Client HTTP avec axios

#### Pages
- **Home**: Page d'accueil avec vérification API
- **Dashboard**: Tableau de bord principal

### Backend

#### Structure
```
app/
├── main.py              # Application FastAPI
├── config.py            # Configuration centralisée
├── database/
│   └── db.py           # SQLAlchemy setup
├── models/
│   ├── models.py       # SQLAlchemy ORM
│   └── schemas.py      # Pydantic schemas
├── agents/
│   ├── cfo_agent.py      # Agent d'analyse
│   └── strategist_agent.py # Agent d'investissement
└── routes/
    ├── health.py       # Health check
    └── analysis.py     # API d'analyse
```

#### Agents LangChain

**CFO Agent**
- Model: Gemini 2.5 Flash
- Input: Données de dépenses (list[dict])
- Output: Analyse structurée
  - summary
  - trends
  - recommendations
  - total_expenses
  - average_daily_expense

**Strategist Agent**
- Model: Gemini 2.5 Flash
- Input: total_expenses, trends, recommendations
- Output: 3 scénarios
  - Conservative (3-5% return, low risk)
  - Balanced (6-8% return, medium risk)
  - Growth (8-10% return, high risk)

### Database

#### Schema

**Users**
```
id: int (PK)
email: str (UNIQUE)
username: str (UNIQUE)
hashed_password: str
created_at: timestamp
updated_at: timestamp
```

**Analyses**
```
id: int (PK)
user_id: int (FK)
filename: str
expense_data: json
cfo_analysis: text (JSON)
trends: json
created_at: timestamp
```

**InvestmentScenarios**
```
id: int (PK)
analysis_id: int (FK)
scenario_number: int
title: str
description: str
expected_return: float
risk_level: str
details: json
created_at: timestamp
```

## Flux API

### POST /api/analysis/upload-file
```
Request:
  - file: FormData (CSV/Excel)

Processing:
  1. Parse fichier → DataFrame
  2. Convert to list[dict]
  3. CFO Agent.analyze()
  4. Save to DB

Response:
  {
    "analysis_id": 1,
    "cfo_analysis": {...},
    "filename": "expenses.csv"
  }
```

### POST /api/analysis/generate-scenarios/{analysis_id}
```
Request:
  - analysis_id: int (path param)

Processing:
  1. Fetch analysis from DB
  2. Extract metrics
  3. Strategist Agent.generate()
  4. Save scenarios to DB

Response:
  {
    "analysis_id": 1,
    "scenarios": [...],
    "market_comparison": {...}
  }
```

## Déploiement Docker

### Services
1. **postgres**: Base de données
2. **backend**: API FastAPI
3. **frontend**: App React

### Networks
- All services on `finova_network`
- Port mapping:
  - 5432 → DB
  - 8000 → Backend
  - 3000 → Frontend

### Volumes
- `postgres_data`: Persistence de la DB
- `./backend`: Source code hot-reload
- `./frontend`: Source code hot-reload
- `/app/node_modules`: Cache npm

## Configuration

### Environnement
- `DATABASE_URL`: Connection string PostgreSQL
- `GEMINI_API_KEY`: Google API key
- `ENVIRONMENT`: development/production
- `REACT_APP_API_URL`: Backend URL pour frontend

### CORS
- Origins autorisées: localhost:3000, localhost:8000
- Credentials: enabled
- Methods: all
- Headers: all

## Scalabilité Future

### Améliorations possibles
1. Authentication JWT
2. Caching (Redis)
3. Queue (Celery/RabbitMQ)
4. Multiple LLM providers
5. Websockets pour temps réel
6. API rate limiting
7. Monitoring (Prometheus, Grafana)
8. Logging centralisé (ELK)

## Sécurité

### En place
- CORS configuré
- Environment variables
- SQLAlchemy ORM (protection SQL injection)
- Pydantic validation
- Hash passwords

### À ajouter (production)
- HTTPS/SSL
- JWT authentication
- Rate limiting
- CSRF protection
- Input sanitization
- Error handling renforcé

---

Architecture robuste et scalable pour l'analyse financière avec IA! 🚀
