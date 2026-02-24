# Finova - Plateforme d'Analyse Financière Intelligente

Finova est une application web complète pour l'analyse financière utilisant des agents IA (LangChain + Gemini 2.5 Flash). Elle permet d'uploader des fichiers de dépenses et de recevoir une analyse détaillée avec des scénarios d'investissement.

## 🎯 Fonctionnalités

### Agent CFO
- Analyse automatique des fichiers CSV/Excel
- Extraction des tendances de dépenses
- Identification des catégories principales
- Calcul des moyennes et totaux
- Recommandations d'optimisation

### Agent Strategist
- Génération de 3 scénarios d'investissement
- Comparaison avec les rendements du marché
- Analyse des risques (Faible, Modéré, Élevé)
- Recommandations personnalisées

### Interface
- Design Dark Mode épuré et moderne
- Graphiques en temps réel (Recharts)
- Upload par drag-and-drop
- Visualisation des analyses

## 🏗️ Architecture

```
Finova/
├── docker-compose.yml          # Orchestration des services
├── .env.example                # Variables d'environnement
│
├── frontend/                   # React + Tailwind + Shadcn/UI
│   ├── Dockerfile
│   ├── src/
│   │   ├── components/         # Composants réutilisables
│   │   ├── pages/              # Pages principales
│   │   ├── hooks/              # Custom hooks
│   │   └── App.jsx
│   └── package.json
│
├── backend/                    # FastAPI + LangChain + PostgreSQL
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py             # Application FastAPI
│   │   ├── config.py           # Configuration
│   │   ├── agents/             # Agents LangChain (CFO, Strategist)
│   │   ├── models/             # SQLAlchemy models et schemas Pydantic
│   │   ├── routes/             # API routes
│   │   └── database/           # Configuration DB
│   └── .env
│
└── postgres/                   # Base de données PostgreSQL
```

## 🚀 Démarrage Rapide

### Prérequis
- Docker & Docker Compose
- Clé API Google Gemini (gratuite)

### Installation

1. **Cloner le projet**
```bash
cd /Users/mory_jr/Finova
```

2. **Configurer les variables d'environnement**
```bash
cp .env.example .env
# Éditez .env et ajoutez votre GEMINI_API_KEY
```

3. **Lancer l'application**
```bash
docker-compose up --build
```

L'application sera disponible à:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Docs API: http://localhost:8000/docs

## 📊 Utilisation

1. **Page d'accueil**: Vérification de la connexion avec l'API
2. **Tableau de bord**: 
   - Téléchargez un fichier CSV/Excel avec vos dépenses
   - L'Agent CFO analyse automatiquement les données
   - L'Agent Strategist génère 3 scénarios d'investissement
3. **Visualisations**: Graphiques des dépenses et tendances

## 📁 Format de Fichier Accepté

CSV ou Excel avec colonnes:
```
category,amount,date
Alimentation,45.50,2024-01-15
Transport,20.00,2024-01-15
Loisirs,30.00,2024-01-16
```

## 🤖 Agents IA

### CFO Agent
**Rôle**: Expert en analyse financière
**Actions**:
- Analyse les dépenses par catégorie
- Identifie les tendances principales
- Propose des recommandations d'optimisation
- Calcule les métriques clés

### Strategist Agent
**Rôle**: Conseiller en investissement
**Actions**:
- Crée 3 scénarios avec risques différents
- Compare avec les rendements du marché
- Propose des allocations de portefeuille
- Tient compte de l'inflation

## 🔧 API Endpoints

### Analysis
- `POST /api/analysis/upload-file` - Upload et analyse un fichier
- `GET /api/analysis/analysis/{id}` - Récupère une analyse
- `POST /api/analysis/generate-scenarios/{id}` - Génère les scénarios
- `GET /api/analysis/scenarios/{id}` - Récupère les scénarios

### Health
- `GET /api/health/` - Vérification de l'état

## 🗄️ Base de Données

### Tables
- **users**: Profils utilisateurs
- **analyses**: Historique des analyses
- **investment_scenarios**: Scénarios générés

## 🔐 Configuration

### Variables d'Environnement
```
# Backend
DATABASE_URL=postgresql://user:password@host:port/db
GEMINI_API_KEY=your_key_here
ENVIRONMENT=development

# Frontend
REACT_APP_API_URL=http://localhost:8000

# Database
DB_USER=finova
DB_PASSWORD=finova123
DB_NAME=finova_db
```

## 📦 Dépendances Principales

### Frontend
- React 18
- Tailwind CSS
- Shadcn/UI
- Recharts
- Axios

### Backend
- FastAPI
- SQLAlchemy
- LangChain
- Google Generative AI
- Pandas
- PostgreSQL

## 🐳 Docker

### Build & Run
```bash
# Build les images
docker-compose build

# Lancer les services
docker-compose up

# Arrêter les services
docker-compose down

# Voir les logs
docker-compose logs -f
```

## ⚠️ Troubleshooting

### Erreur de connexion API
- Vérifiez que les ports (3000, 8000, 5432) sont libres
- Vérifiez le fichier `.env`
- Consultez les logs: `docker-compose logs`

### Erreur Gemini API
- Vérifiez votre clé API
- Vérifiez la limite de requêtes
- Consultez: https://ai.google.dev

### Erreur Base de Données
- Vérifiez que PostgreSQL démarre correctement
- Vérifiez les identifiants dans `.env`
- Réinitialisez les volumes: `docker-compose down -v`

## 📚 Ressources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [LangChain Documentation](https://docs.langchain.com)
- [Gemini API](https://ai.google.dev)
- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)

## 📝 Licence

MIT License

## 👤 Auteur

Finova - Application d'Analyse Financière Intelligente
