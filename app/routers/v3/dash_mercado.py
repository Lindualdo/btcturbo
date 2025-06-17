# app/routers/v3/dash_mercado.py

from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/dash-mercado")
async def calcular_dash_mercado():
    """
    Calcula e grava scores consolidados do mercado BTC
    
    Fluxo:
    1. Coleta dados dos 3 blocos (ciclo, momentum, técnico)
    2. Calcula scores individuais
    3. Calcula score consolidado
    4. Grava no banco
    """
    try:
        from app.services.v3.dash_mercado.dash_mercado_service  import calcular_dashboard_mercado
        
        logger.info("🚀 Calculando Dashboard Mercado...")
        resultado = calcular_dashboard_mercado()
        
        if resultado.get("status") == "success":
            logger.info("✅ Dashboard Mercado calculado com sucesso")
            return resultado
        else:
            logger.error(f"❌ Erro calcular dashboard: {resultado.get('erro')}")
            raise HTTPException(status_code=500, detail=resultado.get("erro"))
            
    except Exception as e:
        logger.error(f"❌ Erro endpoint POST dash-mercado: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dash-mercado")
async def obter_dash_mercado():
    """
    Obtém último score consolidado do dashboard mercado
    """
    try:
        from app.services.v2.dash_mercado_service import obter_dashboard_mercado
        
        resultado = obter_dashboard_mercado()
        
        if resultado.get("status") == "success":
            return resultado
        else:
            raise HTTPException(status_code=404, detail="Dashboard não encontrado")
            
    except Exception as e:
        logger.error(f"❌ Erro endpoint GET dash-mercado: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dash-mercado/debug")
async def debug_dash_mercado():
    """
    Debug do sistema dashboard mercado
    """
    try:
        from app.services.v2.dash_mercado_service import debug_dashboard_mercado
        
        return debug_dashboard_mercado()
        
    except Exception as e:
        logger.error(f"❌ Erro debug dash-mercado: {str(e)}")
        return {
            "status": "error",
            "erro": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }