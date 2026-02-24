# Commandes Finova

## 🚀 Démarrage

### Setup Initial
```bash
# 1. Copier la config
cp .env.example .env

# 2. Ajouter votre clé Gemini dans .env
# GEMINI_API_KEY=votre_clé_ici

# 3. Build et lancer
docker-compose up --build

# ✅ App accessible à:
#    Frontend: http://localhost:3000
#    Backend:  http://localhost:8000
#    Docs API: http://localhost:8000/docs
```

## 📋 Gestion Services

### Services
```bash
# Lancer tout
docker-compose up

# Lancer en background
docker-compose up -d

# Arrêter
docker-compose down

# Arrêter et supprimer volumes (réinitialiser DB)
docker-compose down -v

# Rebuild images
docker-compose up --build

# Rebuil une image spécifique
docker-compose build backend
docker-compose build frontend
```

## 📊 Logs

```bash
# Tous les logs
docker-compose logs -f

# Logs backend uniquement
docker-compose logs -f backend

# Logs frontend uniquement
docker-compose logs -f frontend

# Logs DB uniquement
docker-compose logs -f postgres

# Dernières 100 lignes
docker-compose logs -f --tail 100 backend
```

## 🛠️ Développement

### Backend

```bash
# Shell du backend
docker-compose exec backend bash

# Python shell
docker-compose exec backend python

# Accéder à l'API
curl http://localhost:8000/api/health/

# Voir la doc
open http://localhost:8000/docs

# Tests (futur)
docker-compose exec backend pytest
```

### Frontend

```bash
# Shell du frontend
docker-compose exec frontend bash

# Installer une dépendance
docker-compose exec frontend npm install axios

# Build de production
docker-compose exec frontend npm run build
```

## 🗄️ Base de Données

```bash
# Accéder à psql
docker-compose exec postgres psql -U finova -d finova_db

# Commandes utiles psql:
# \dt                     - Lister les tables
# \d nom_table           - Décrire une table
# SELECT * FROM analyses; - Voir les analyses
# \q                     - Quitter

# Backup de la DB
docker-compose exec postgres pg_dump -U finova finova_db > backup.sql

# Restore de la DB
docker-compose exec postgres psql -U finova finova_db < backup.sql
```

## 📝 Fichiers à Connaître

```
.env                    - Configuration (à remplir avec votre clé)
docker-compose.yml      - Orchestration des services
backend/requirements.txt - Dépendances Python
frontend/package.json   - Dépendances Node
```

## 🔑 Variables Importantes

```bash
# Dans .env:
GEMINI_API_KEY=your_key_here           # ⚠️ À remplir!
DATABASE_URL=postgresql://...          # Connection DB
ENVIRONMENT=development                 # Dev ou production
REACT_APP_API_URL=http://localhost:8000 # URL backend pour frontend
```

## 📱 Utilisation Typique

### Workflow User
1. Ouvrir http://localhost:3000
2. Voir message "API connectée" ✓
3. Cliquer "Accéder au Tableau de Bord"
4. Télécharger un fichier CSV/Excel
5. Attendre l'analyse CFO (2-5 sec)
6. Voir les résultats et graphiques
7. Attendre la génération des scénarios
8. Explorer les 3 scénarios d'investissement

### Fichier Exemple
```csv
category,amount,date
Alimentation,45.50,2024-01-15
Transport,20.00,2024-01-15
Loisirs,30.00,2024-01-16
```

Voir `example_expenses.csv` pour exemple complet.

## 🐛 Troubleshooting

### Port déjà utilisé
```bash
# Trouver le process
lsof -i :3000
lsof -i :8000
lsof -i :5432

# Tuer le process
kill -9 <PID>
```

### DB ne démarre pas
```bash
# Supprimer et recommencer
docker-compose down -v
docker-compose up --build
```

### Frontend blanc
```bash
# Vérifier les logs
docker-compose logs frontend

# Rebuild
docker-compose down
docker-compose up --build frontend
```

### Erreur API Gemini
```bash
# Vérifier la clé dans .env
# Vérifier sur https://ai.google.dev que la clé est active
# Vérifier votre quota/limite
```

## 📚 Documentation Complète

```
README.md        - Overview & features
QUICKSTART.md    - Démarrage rapide
ARCHITECTURE.md  - Détails architecture
TECH_STACK.md    - Technologies utilisées
DATABASE.md      - Schema base de données
LIVRABLES.md     - Checklis des livrables
COMMANDS.md      - Ce fichier!
```

## 🎯 API Endpoints

```bash
# Health check
GET http://localhost:8000/api/health/

# Uploader un fichier
POST http://localhost:8000/api/analysis/upload-file
Body: FormData(file)

# Récupérer une analyse
GET http://localhost:8000/api/analysis/analysis/{id}

# Générer les scénarios
POST http://localhost:8000/api/analysis/generate-scenarios/{id}

# Récupérer les scénarios
GET http://localhost:8000/api/analysis/scenarios/{id}

# Documentation interactive
GET http://localhost:8000/docs
```

## 🔄 Workflow Développement

### Modification Backend
```bash
# Les changements sont automatiquement rechargés (--reload)
# Éditez app/ et sauvegardez
# API recharge automatiquement
```

### Modification Frontend
```bash
# Les changements sont automatiquement rechargés
# Éditez src/ et sauvegardez
# Browser recharge automatiquement
```

### Modification Requirements
```bash
# Ajouter une dépendance
echo "nouvelle-lib==1.0" >> backend/requirements.txt

# Rebuild backend
docker-compose up --build backend
```

### Modification Package.json
```bash
# Ajouter une dépendance
docker-compose exec frontend npm install nouvelle-lib

# Rebuild frontend
docker-compose up --build frontend
```

## 🚀 Déploiement Préparation

### Avant de déployer:
```bash
# 1. Créer un .env.production
cp .env.example .env.production

# 2. Mettre à jour les variables
ENVIRONMENT=production
DATABASE_URL=votre_db_production
GEMINI_API_KEY=votre_clé

# 3. Build images de production
docker-compose -f docker-compose.yml build

# 4. Test en production local
ENVIRONMENT=production docker-compose up
```

## 📊 Monitoring

### Health Check
```bash
# Vérifier que l'API répond
curl http://localhost:8000/api/health/

# Réponse attendue:
# {"status":"ok","service":"Finova API"}
```

### Vérifier les services
```bash
# Liste des conteneurs
docker-compose ps

# Statistiques de ressource
docker stats
```

---

💡 **Tip**: Mettez `COMMANDS.md` en favoris pour accès rapide!

Bonne utilisation! 🎉
