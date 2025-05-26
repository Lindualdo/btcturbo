#app/routers/analise_ciclos.py

from fastapi import APIRouter
from datetime import datetime
from app.services.blocos import ciclo

router = APIRouter()

@router.get("/analise-ciclo")
def analisar_ciclo():
    return ciclo.calcular_bloco_ciclo()