# app/routers/analise_risco.py - REFATORADO

from fastapi import APIRouter
from app.services.analises.analise_risco import calcular_analise_risco

router = APIRouter()

@router.get("/analise-risco")
async def analisar_risco():
    """
    API da Camada 2: Gestão de Risco
    
    Usa dados já calculados de /calcular-score/riscos
    """
    return calcular_analise_risco()