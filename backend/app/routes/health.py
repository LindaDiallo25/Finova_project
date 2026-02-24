from fastapi import APIRouter

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("/")
async def health_check():
    """Vérification de l'état de l'API"""
    return {"status": "ok", "service": "Finova API"}
