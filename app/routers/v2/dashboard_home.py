# app/routers/v2/dashboard_home.py

from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging
from app.services.v2.dashboard_home_service import (
    calcular_dashboard_v2, 
    obter_dashboard_v2,
    debug_dashboard_v2
)

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/dashboard-home")
async def calcular_dashboard_home_v2():
    """
    POST /api/v2/dashboard-home
    Calcula dashboard otimizado com busca única de dados
    """
    try:
        logger.info("🚀 POST Dashboard V2 - Iniciando...")
        resultado = calcular_dashboard_v2()
        
        if resultado["status"] == "error":
            raise HTTPException(status_code=400, detail=resultado)
        
        return resultado
        
    except Exception as e:
        logger.error(f"❌ Erro POST dashboard V2: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "erro": str(e),
            "message": "Falha no cálculo dashboard V2"
        })

@router.get("/dashboard-home")
async def obter_dashboard_home_v2():
    """
    GET /api/v2/dashboard-home  
    Retorna último dashboard V2 calculado
    """
    try:
        logger.info("🔍 GET Dashboard V2 - Buscando...")
        resultado = obter_dashboard_v2()
        
        if resultado["status"] == "error":
            raise HTTPException(status_code=404, detail=resultado)
        
        return resultado
        
    except Exception as e:
        logger.error(f"❌ Erro GET dashboard V2: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "status": "error", 
            "erro": str(e),
            "message": "Falha ao obter dashboard V2"
        })

@router.get("/dashboard-home/debug")
async def debug_dashboard_home_v2():
    """
    GET /api/v2/dashboard-home/debug
    Debug do sistema V2
    """
    try:
        return debug_dashboard_v2()
    except Exception as e:
        logger.error(f"❌ Erro debug V2: {str(e)}")
        return {
            "status": "error",
            "erro": str(e),
            "versao": "v2"
        }