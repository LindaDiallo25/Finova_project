# Finova - Stack Technologique

## Frontend
- **React 18** - Librairie UI
- **Tailwind CSS** - Utility-first CSS
- **Shadcn/UI** - Composants épurés
- **Recharts** - Graphiques interactifs
- **React Router** - Routing
- **Axios** - Client HTTP
- **React Dropzone** - Upload files

## Backend
- **FastAPI** - Framework web async
- **Uvicorn** - ASGI server
- **SQLAlchemy** - ORM
- **Pydantic** - Validation data
- **LangChain** - Framework IA
- **Google Generative AI** - LLM (Gemini 2.5 Flash)
- **Pandas** - Data processing
- **Python-Jose** - JWT tokens
- **Passlib** - Password hashing

## Database
- **PostgreSQL** - Base de données
- **psycopg2** - Driver PostgreSQL

## DevOps
- **Docker** - Conteneurization
- **Docker Compose** - Orchestration

## Outils de Développement
- **VS Code** - Éditeur
- **Git** - Version control
- **Postman** - API testing (optionnel)

## Versions de Production Recommandées

```yaml
Frontend:
  node: "18.x"
  npm: "9.x"

Backend:
  python: "3.11"
  pip: "23.x"

Database:
  postgresql: "15"

Docker:
  docker: "24.x"
  compose: "2.x"
```

## Performance Optimization

### Frontend
- Code splitting avec React.lazy()
- Image optimization
- CSS minification (build)
- Tree shaking

### Backend
- Connection pooling (SQLAlchemy)
- Query optimization
- Caching (future)
- Async endpoints

### Database
- Index sur user_id, analysis_id
- Connection pooling
- Auto-vacuum configuré

## Monitoring & Logging

### Frontend
- Console.log (développement)
- Sentry (production, optionnel)

### Backend
- Uvicorn logging
- SQLAlchemy logging
- Custom log handlers

## Next Steps

Pour la production:
1. Setup CI/CD (GitHub Actions)
2. Ajouter tests (pytest, Jest)
3. Setup monitoring (Sentry, DataDog)
4. Configurer secrets manager
5. Implémenter caching (Redis)
6. Ajouter rate limiting
7. Setup logging centralisé
