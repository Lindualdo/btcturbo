
from fastapi import APIRouter
from app.services.tendencia.tendecia_service import calcular_score

router = APIRouter()

@router.get("/calcular_score_tendecia")
async def calcular_score():
        return calcular_score()
  