# app/routers/analise_mercado.py - REFATORADO

from fastapi import APIRouter
from app.services.analises.analise_mercado import calcular_analise_mercado

router = APIRouter()

@router.get("/analise-mercado")
async def analisar_mercado():
    """
    API da Camada 1: Análise de Mercado
    
    Consolida scores dos blocos Ciclo (50%) + Técnico (30%) + Momentum (20%)
    Retorna se mercado está favorável para posicionamento
    """
    return calcular_analise_mercado()
