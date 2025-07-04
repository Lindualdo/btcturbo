
from fastapi import APIRouter
from app.services.tendencia import tendecia_service

router = APIRouter()

@router.get("/calcular-score-tendecia")
async def calcular_score():
        return  tendecia_service.calcular_score()
  