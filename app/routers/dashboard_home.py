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
    FASE 3: Calcula e grava dados do dashboard home (header + mercado + risco)
    
    Returns:
        JSON com status da operação
    """
    return calcular_dashboard_home()

@router.get("/dashboard-home")
async def obter_dados_dashboard_home():
    """
    FASE 3: Obtém dados do dashboard home do PostgreSQL
    
    Returns:
        JSON do dashboard com 3 módulos
    """
    return obter_dashboard_home()

@router.get("/dashboard-home/debug")
async def debug_dados_dashboard_home():
    """
    Debug simples do dashboard home
    
    Returns:
        Informações básicas de debug
    """
    return debug_dashboard_home()