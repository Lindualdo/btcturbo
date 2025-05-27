#/app/routers/indicadores.py

from fastapi import APIRouter
from datetime import datetime
from app.services.indicadores import ciclo, riscos, momentum, tecnico

router = APIRouter()

@router.get("/api/v1/indicadores/{bloco}")
async def obter_indicadores(bloco: str):
    if bloco == "ciclo":
        return ciclo.obter_indicadores()
    elif bloco == "riscos":
        return riscos.obter_indicadores()
    elif bloco == "momentum":
        return momentum.obter_indicadores()
    elif bloco == "tecnico":
        return tecnico.obter_indicadores()
    else:
        return {"status": "erro", "detalhes": "Bloco inválido"}

