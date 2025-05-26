from fastapi import APIRouter
from app.services.blocos import ciclo

router = APIRouter()

@router.get("/")
def analise_geral():
    score_ciclo = ciclo.calcular_bloco_ciclo()
    return {
        "score_final": 5.0,
        "blocos": {
            "ciclo": score_ciclo
        }
    }