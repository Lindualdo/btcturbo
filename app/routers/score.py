# app/routers/score.py

from fastapi import APIRouter
from app.services.scores import ciclos, momentum, riscos, tecnico

router = APIRouter()

@router.get("/calcular-score/{bloco}")
async def calcular_score(bloco: str):
    if bloco == "ciclos":
        return ciclos.calcular_score()
    elif bloco == "momentum":
        return momentum.calcular_score()
    elif bloco == "riscos":
        return riscos.calcular_score()
    elif bloco == "tecnico":
        return tecnico.calcular_score()
    else:
        return {
            "status": "erro", 
            "detalhes": f"Bloco '{bloco}' inválido. Blocos disponíveis: ciclos, momentum, riscos, tecnico"
        }