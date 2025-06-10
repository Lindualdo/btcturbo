# app/routers/dashboard_home.py

from fastapi import APIRouter
from app.services.dashboard.home import (
    calcular_dashboard_home, 
    obter_dashboard_home,
    debug_dashboard_home
)

router = APIRouter()

@router.post("/dashboard-home")
async def calcular_dados_dashboard_home():
    """
    FASE 2: Calcula e grava dados do dashboard home (cabeçalho + score mercado)
    
    Fluxo:
    1. Busca dados de /obter-indicadores/riscos
    2. Busca dados de /analise-mercado
    3. Busca dados de /obter-indicadores/ciclos
    4. Extrai: btc_price, position_dolar, alavancagem_atual, score_mercado, mvrv, nupl
    5. Calcula: position_btc = position_dolar / btc_price
    6. Monta JSON do dashboard
    7. Grava no PostgreSQL
    
    Returns:
        JSON com status da operação
    """
    return calcular_dashboard_home()

@router.get("/dashboard-home")
async def obter_dados_dashboard_home():
    """
    FASE 2: Obtém dados do dashboard home do PostgreSQL
    
    Retorna JSON pronto para o frontend consumir.
    Dados já processados e formatados (cabeçalho + score mercado).
    
    Returns:
        JSON do dashboard ou erro se não houver dados
    """
    return obter_dashboard_home()

@router.get("/dashboard-home/debug")
async def debug_dados_dashboard_home():
    """
    FASE 2: Debug simples do dashboard home
    
    Útil para verificar:
    - Se tem dados
    - Último registro inserido
    
    Returns:
        Informações básicas de debug
    """
    return debug_dashboard_home()