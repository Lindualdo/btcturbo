#/app/routers/indicadores.py

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/indicadores/{bloco}")
async def obter_indicadores(bloco: str):
    if bloco == "ciclo":
        return {
            "bloco": "ciclo",
            "timestamp": datetime.utcnow().isoformat(),
            "indicadores": {
                "MVRV_Z": {"valor": 2.1, "fonte": "Glassnode"},
                "Realized_Ratio": {"valor": 1.3, "fonte": "Glassnode"},
                "Puell_Multiple": {"valor": 1.2, "fonte": "Glassnode"}
            }
        }
    return {"status": "erro", "detalhes": "Bloco inválido"}
