
from fastapi import APIRouter
from app.services.tendencia.tendecia_service import calcular_score

from fastapi import APIRouter
from app.services.coleta import ciclos, riscos, momentum

router = APIRouter()

@router.get("/calcular_score_tendecia")
async def coletar_indicadores():
        return calcular_score()
  