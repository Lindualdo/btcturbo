from fastapi import APIRouter
from app.services.scores import riscos
from app.services.alavancagem.alavancagem_service import calcular_alavancagem

router = APIRouter()

@router.get("/score-risco")
async def calcular_score():
   return riscos.calcular_score_compacto


@router.get("/alavancagem")
async def get_alavancagem():
    return calcular_alavancagem()