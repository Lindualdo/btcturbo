#/app/routers/coleta.py

from fastapi import APIRouter
from app.services.coleta import ciclos, riscos, momentum, tecnico

from fastapi import APIRouter
from app.services.coleta import ciclos, riscos, momentum, tecnico

router = APIRouter()

@router.post("/coletar-indicadores/{bloco}")
async def coletar_indicadores(bloco: str, forcar_coleta: bool = False):
    if bloco == "ciclos":
       return {"status": "erro", "detalhes": "Está sendo importado no N8N"}
    elif bloco == "riscos":
        return riscos.coletar(forcar_coleta)
    elif bloco == "momentum":
        return {"status": "erro", "detalhes": "Está sendo importado no N8N"}
    elif bloco == "tecnico":
        return tecnico.coletar(forcar_coleta)
    else:
        return {"status": "erro", "detalhes": "Bloco inválido"}
