from fastapi import APIRouter
from datetime import datetime
from app.services.blocos import ciclo

router = APIRouter()

@router.get("/")
def analisar_ciclo():
    return ciclo.calcular_bloco_ciclo()