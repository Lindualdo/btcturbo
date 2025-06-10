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
    FASE 1: Calcula e grava dados do dashboard home (apenas cabeçalho)
    
    Fluxo:
    1. Busca dados de /obter-indicadores/riscos
    2. Extrai: btc_price, position_dolar, alavancagem_atual
    3. Calcula: position_btc = position_dolar / btc_price
    4. Monta JSON do dashboard
    5. Grava no PostgreSQL
    
    Returns:
        JSON com status da operação
    """
    return calcular_dashboard_home()

@router.get("/dashboard-home")
async def obter_dados_dashboard_home():
    """
    FASE 1: Obtém dados do dashboard home do PostgreSQL
    
    Retorna JSON pronto para o frontend consumir.
    Dados já processados e formatados.
    
    Returns:
        JSON do dashboard ou erro se não houver dados
    """
    return obter_dashboard_home()

@router.get("/dashboard-home/debug")
async def debug_dados_dashboard_home():
    """
    FASE 1: Debug e estatísticas do dashboard home
    
    Útil para verificar:
    - Se tabela existe
    - Quantos registros tem
    - Último registro inserido
    - Médias dos valores
    
    Returns:
        Estatísticas e informações de debug
    """
    return debug_dashboard_home()