#app/routers/analise.py

from fastapi import APIRouter
from datetime import datetime
from app.services import alertas 

router = APIRouter()

@router.get("/analise-btc")
async def analise_btc():
    # Exemplo consolidado mockado simplificado
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "score_final": 5.85,
        "classificacao_geral": "Neutro",
        "kelly_allocation": "25%",
        "acao_recomendada": "Manter posição conservadora",
        "alertas_ativos": alertas["alertas_ativos"],
        "blocos": {
            "ciclo": {"score": 5.5, "peso": "40%"},
            "momentum": {"score": 6.2, "peso": "25%"},
            "risco": {"score": 5.0, "peso": "15%"},
            "tecnico": {"score": 6.5, "peso": "20%"}
        }
    }