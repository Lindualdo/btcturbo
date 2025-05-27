#/app/routers/coleta.py

from fastapi import APIRouter
from services.coleta import ciclo, riscos, momentum, tecnico

router = APIRouter()

@router.post("/coletar-indicadores")
async def coletar_indicadores(bloco: str, forcar_coleta: bool = False):
    if bloco == "ciclo":
        return ciclo.coletar(forcar_coleta)
    elif bloco == "riscos":
        return riscos.coletar(forcar_coleta)
    elif bloco == "momentum":
        return momentum.coletar(forcar_coleta)
    elif bloco == "tecnico":
        return tecnico.coletar(forcar_coleta)
    else:
        return {"status": "erro", "detalhes": "Bloco inválido"}