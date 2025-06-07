# app/routers/alertas_debug.py - CORRIGIDO (SEM INVENÇÕES)

from fastapi import APIRouter
from app.services.alertas.debug_service import AlertasDebugService

router = APIRouter()
debug_service = AlertasDebugService()

@router.get("/criticos", summary="Debug Alertas Críticos")
async def debug_alertas_criticos():
    """
    Debug categoria CRÍTICOS - Proteção imediata
    - Health Factor < 1.3
    - Distância Liquidação < 20%
    - Score Risco < 30
    - Portfolio Loss 24h > 20%
    - Leverage > MVRV Max * 1.2
    """
    return debug_service.debug_criticos()

@router.get("/urgentes", summary="Debug Alertas Urgentes")
async def debug_alertas_urgentes():
    """
    Debug categoria URGENTES - Avisos preventivos
    - Health Factor < 1.5
    - Distância Liquidação < 30%
    - Score Risco < 50
    """
    return debug_service.debug_urgentes()

@router.get("/volatilidade", summary="Debug Alertas Volatilidade")
async def debug_alertas_volatilidade():
    """
    Debug categoria VOLATILIDADE - Timing e breakouts
    - BBW < 10% por 5+ dias
    - Volume spike > 200%
    - ATR < 2.0%
    - EMA144 > 15% + RSI > 65
    - Pump & Drift detectado
    """
    return debug_service.debug_volatilidade()

@router.get("/geral", summary="Debug Geral - Todas Categorias")
async def debug_alertas_geral():
    """
    Overview completo do sistema de alertas
    Status de todas as categorias implementadas
    """
    return debug_service.debug_geral()

# Endpoints TODO - próximas implementações
@router.get("/taticos", summary="Debug Alertas Tático")
async def debug_alertas_taticos():
    """TODO: Entradas/saídas específicas"""
    
    """
    - EMA144 < -8% + RSI < 40 (compra)",
    - Score mercado > 70 + leverage baixo (aumentar)",
    - EMA144 > 15% + 5 dias green (parcial)",
    - Matriz tática breakout",
    - DCA opportunity",
    - Funding negativo + preço estável"
    """

    return debug_service.debug_tatico()


@router.get("/onchain", summary="Debug Alertas OnChain [TODO]")
async def debug_alertas_onchain():
    """TODO: Baleias, divergências, smart money"""
    return {
        "categoria": "ONCHAIN", 
        "status": "TODO",
        "alertas_planejados": [
            "Exchange whale ratio > 85%",
            "Dormancy flow > 500k",
            "Miners to exchanges > threshold",
            "Divergência preço vs netflow",
            "Funding negativo + preço estável"
        ]
    }