# app/routers/alertas_debug.py

from fastapi import APIRouter
from app.services.alertas.debug_service import AlertasDebugService

router = APIRouter()
debug_service = AlertasDebugService()

@router.get("/critico", summary="Debug Alertas Críticos (Posição)")
async def debug_alertas_posicao():
    """
    Debug categoria CRÍTICOS - Posição
    - Health Factor < 1.3
    - Score Risco < 30  
    - Distância Liquidação < 20%
    - Portfolio Loss 24h > 20%
    - Leverage > MVRV Max * 1.2
    """
    return debug_service.debug_criticos()


@router.get("/volatilidade", summary="Debug Alertas Volatilidade")
async def debug_alertas_volatilidade():
    """
    Debug categoria VOLATILIDADE
    - BBW < 5% por 7+ dias (crítico)
    - Volume spike > 300% (urgente)
    - ATR mínimo < 1.5% (urgente)
    - EMA144 + RSI realizações (informativo)
    - Pump & Drift patterns (informativo)
    """
    return debug_service.debug_volatilidade()

@router.get("/geral", summary="Debug Geral - Todas Categorias")
async def debug_alertas_geral():
    """
    Overview completo do sistema de alertas
    Status de todas as categorias implementadas
    """
    return debug_service.debug_geral()

# Endpoints TODO - implementar próximas iterações
@router.get("/mercado", summary="Debug Alertas Mercado [TODO]")
async def debug_alertas_mercado():
    """TODO: MVRV extremos, mudanças regime, RSI semanal"""
    return {
        "categoria": "MERCADO",
        "status": "TODO",
        "alertas_planejados": [
            "MVRV > 5 (topo zone)",
            "Score mercado mudou 20+ pontos",
            "RSI semanal > 75 + RSI diário > 75",
            "Funding rate 7d > 0.15%"
        ]
    }

@router.get("/tatico", summary="Debug Alertas Tático [TODO]") 
async def debug_alertas_tatico():
    """TODO: Entradas/saídas específicas"""
    return {
        "categoria": "TÁTICO",
        "status": "TODO",
        "alertas_planejados": [
            "EMA144 < -8% + RSI < 40 (compra)",
            "Score mercado > 70 + leverage baixo (aumentar)",
            "Matriz tática breakouts",
            "DCA opportunities"
        ]
    }

@router.get("/onchain", summary="Debug Alertas OnChain [TODO]")
async def debug_alertas_onchain():
    """TODO: Baleias, divergências, netflow"""
    return {
        "categoria": "ONCHAIN", 
        "status": "TODO",
        "alertas_planejados": [
            "Exchange whale ratio > 85%",
            "Dormancy flow > 500k",
            "Divergências preço vs netflow",
            "Miners to exchanges"
        ]
    }