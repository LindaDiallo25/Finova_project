# 🚀 Guide de Démarrage - Finova

## ✅ Prérequis

- Docker & Docker Compose installés
- Clé API Google Gemini (gratuite sur https://ai.google.dev)
- Navigateur web moderne

## 📋 Installation Rapide

### 1. Cloner/Accéder au projet
```bash
cd /Users/mory_jr/Finova
```

### 2. Créer le fichier .env
```bash
cp .env.example .env
```

### 3. Configurer les variables
Éditez `.env` et remplacez `your_gemini_api_key_here` par votre vraie clé:
```bash
GEMINI_API_KEY=votre_clé_api_ici
```

### 4. Démarrer l'application
```bash
docker-compose up --build
```

## 📍 Accès aux Services

Une fois lancée, l'application est accessible à:

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎮 Utilisation

### Première Utilisation
1. Allez à http://localhost:3000
2. Vérifiez que l'API est connectée (page d'accueil)
3. Cliquez sur "Accéder au Tableau de Bord"

### Analyse des Dépenses
1. Téléchargez un fichier CSV/Excel (voir format ci-dessous)
2. L'Agent CFO analyse automatiquement
3. L'Agent Strategist génère 3 scénarios
4. Explorez les résultats et graphiques

### Format de Fichier

Créez un CSV ou Excel avec ce format:
```
category,amount,date
Alimentation,45.50,2024-01-15
Transport,20.00,2024-01-15
Loisirs,30.00,2024-01-16
Utilities,150.00,2024-01-16
```

## 🔧 Commandes Utiles

### Voir les logs
```bash
docker-compose logs -f
```

### Voir les logs du backend
```bash
docker-compose logs -f backend
```

### Accéder à la base de données
```bash
docker-compose exec postgres psql -U finova -d finova_db
```

### Arrêter l'application
```bash
docker-compose down
```

### Supprimer les données (réinitialiser)
```bash
docker-compose down -v
```

## 🔍 Troubleshooting

### Ports occupés
Si les ports 3000, 8000 ou 5432 sont déjà utilisés:
```bash
# Trouver les processus
lsof -i :3000
lsof -i :8000
lsof -i :5432

# Tuer le processus
kill -9 <PID>
```

### Erreur Gemini API
- Vérifiez votre clé dans `.env`
- Vérifiez que la clé est active sur https://ai.google.dev
- Vérifiez votre quota API

### Frontend ne se charge pas
```bash
# Vérifier les logs
docker-compose logs frontend

# Supprimer et reconstruire
docker-compose down
docker-compose up --build frontend
```

### Base de données ne démarre pas
```bash
# Supprimer les volumes et recommencer
docker-compose down -v
docker-compose up --build
```

## 📚 Architecture

```
Frontend (React)
    ↓ (API HTTP)
Backend (FastAPI)
    ├── Agent CFO
    ├── Agent Strategist
    └── DB (PostgreSQL)
```

## 🤖 Agents IA

### CFO Agent
- Analyse les dépenses
- Extrait les tendances
- Propose des optimisations
- Calcule les métriques

### Strategist Agent  
- Génère 3 scénarios
- Compare au marché
- Évalue les risques
- Propose des allocations

## 🔐 Sécurité

En développement:
- CORS activé pour localhost
- Variables sensibles dans `.env`
- Mot de passe DB par défaut (changez-le en production!)

## 📊 Exemple de Réponse

Une analyse typique retourne:
```json
{
  "cfo_analysis": {
    "summary": "...",
    "trends": ["Augmentation des loisirs", "Réduction de l'alimentation"],
    "recommendations": ["..."],
    "total_expenses": 245.50,
    "average_daily_expense": 61.375
  },
  "scenarios": [
    {
      "title": "Investissement Conservateur",
      "expected_return": 3.5,
      "risk_level": "Faible"
    },
    ...
  ]
}
```

## 🎯 Prochaines Étapes

- [ ] Ajouter l'authentification utilisateurs
- [ ] Implémenter les migrations Alembic
- [ ] Ajouter des tests unitaires
- [ ] Déployer sur le cloud (Vercel, Render, etc.)
- [ ] Ajouter plus d'agents spécialisés
- [ ] Intégrer avec d'autres APIs financières

## 📞 Support

Pour les erreurs:
1. Vérifiez les logs: `docker-compose logs`
2. Consultez la documentation API: http://localhost:8000/docs
3. Vérifiez votre clé Gemini

## 📝 Notes

- Les données sont stockées en base PostgreSQL
- Les analyses sont persistées
- Chaque nouveau fichier crée une nouvelle analyse
- Les scénarios sont générés automatiquement

---

✨ Bienvenue sur Finova!
