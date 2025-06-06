# app/routers/analise_tatica.py

from fastapi import APIRouter
from  app.services.analises.analise_tatica import calcular_analise_tatica

router = APIRouter()

@router.get("/analise-tatica")
async def analisar_tatica():
    """
    API da Camada 4: Análise Tática
    
    Usa matriz EMA144 + RSI Diário para determinar ações específicas
    """
    return calcular_analise_tatica()