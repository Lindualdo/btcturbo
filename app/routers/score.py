#/app/routers/score.py

from fastapi import APIRouter
from app.services.scores import ciclos as ciclo_service

router = APIRouter()

@router.get("/calcular-score/{bloco}")
async def calcular_score(bloco: str):
    if bloco == "ciclos":
        resultado = ciclo_service.calcular_score()
        return resultado
    return {"status": "erro", "detalhes": "Bloco inválido"}
