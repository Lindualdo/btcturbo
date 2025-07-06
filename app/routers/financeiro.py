from fastapi import APIRouter
from app.services.scores import riscos
from app.services.alavancagem import alavancagem_service

router = APIRouter()

@router.get("/score-risco")
async def calcular_score():
   return riscos.calcular_score_compacto


@router.get("/alavancagem")
async def get_alavancagem():
    return alavancagem_service.calcular_alavancagem()