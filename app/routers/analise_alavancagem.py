# app/routers/analise_mercado.py - REFATORADO

from fastapi import APIRouter
from app.services.analises.analise_alavancagem import calcular_analise_alavancagem

router = APIRouter()

@router.get("/analise-alavancagem")
async def analisar_alavancagem():
    """
    API da Camada 3: Análise de Dimensionamento
    
    Usa tabela MVRV × RSI Mensal para determinar alavancagem máxima
    """
    return calcular_analise_alavancagem()