# app/routers/dashboards.py - ADICIONAR ESTES ENDPOINTS

from fastapi import APIRouter, Query
from app.services.dashboards.dash_main_service import processar_dash_main, obter_dash_main
from app.services.dashboards.dash_mercado_service import processar_dash_mercado, obter_dash_mercado
from app.services.dashboards.dash_finance_service import (
    obter_health_factor,
    obter_alavancagem, 
    obter_patrimonio,
    obter_capital_investido
)
from app.services.utils.helpers.postgres.mercado.database_helper import get_ciclo_mercado
from app.services.dashboards.dash_main.analise_alavancagem import executar_analise_alavancagem

router = APIRouter()

# === ENDPOINTS EXISTENTES ===
@router.post("/dash-main")
async def post_dash_main():
    return processar_dash_main()

@router.get("/dash-main")
async def get_dash_main():
    return obter_dash_main()

@router.post("/dash-mercado")
async def post_dash_mercado():
    return processar_dash_mercado()

@router.post("/dash-mercado")
async def post_dash_mercado(aplicar_gatilho: bool = True):
    return processar_dash_mercado(aplicar_gatilho)

@router.get("/dash-mercado/debug")
async def get_dash_mercado_debug():
    return get_ciclo_mercado()

@router.get("/dash-main/alavancagem")
async def get_dash_main_alavancagem():
    dados_mercado = get_ciclo_mercado()
    alavancagem_permitida = dados_mercado["ciclo_detalhes"]["alavancagem"]
    return executar_analise_alavancagem(alavancagem_permitida)

# === NOVOS ENDPOINTS DASH-FINANCE ===

@router.get("/dash-finance/health-factor")
async def get_health_factor(periodo: str = Query(default="30d", description="Período: 30d, 3m, 6m, 1y, all")):
    """Histórico Health Factor (REAL)"""
    return obter_health_factor(periodo)

@router.get("/dash-finance/alavancagem")
async def get_alavancagem(periodo: str = Query(default="30d", description="Período: 30d, 3m, 6m, 1y, all")):
    """Histórico Alavancagem Atual vs Permitida (MOCK)"""
    return obter_alavancagem(periodo)

@router.get("/dash-finance/patrimonio")
async def get_patrimonio(periodo: str = Query(default="30d", description="Período: 30d, 3m, 6m, 1y, all")):
    """Histórico Crescimento Patrimônio Líquido (REAL)"""
    return obter_patrimonio(periodo)

@router.get("/dash-finance/capital-investido")
async def get_capital_investido(periodo: str = Query(default="30d", description="Período: 30d, 3m, 6m, 1y, all")):
    """Histórico Capital Investido - Posição Total (MOCK)"""
    return obter_capital_investido(periodo)