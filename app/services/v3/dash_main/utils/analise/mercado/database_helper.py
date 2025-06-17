# app/routers/v3/dash_main.py

from fastapi import APIRouter, HTTPException
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/dashboard")
async def processar_dashboard_v3():
    """
    Processa Dashboard V3 - 4 Camadas Sequenciais
    
    Sistema: Mercado → Risco → Alavancagem → Tática
    Status: MOCKADO - 100% compatível com V2
    """
    try:
        from app.services.v3.dash_main.dash_home_service import processar_dashboard_v3
        
        resultado = processar_dashboard_v3()
        
        if resultado["status"] == "error":
            raise HTTPException(status_code=500, detail=resultado)
            
        return resultado
        
    except Exception as e:
        logger.error(f"❌ Erro endpoint Dashboard V3: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def obter_dashboard_v3():
    """
    Obtém último Dashboard V3 processado
    """
    try:
        from app.services.v3.dash_main.dash_home_service import obter_dashboard_v3
        
        resultado = obter_dashboard_v3()
        
        if resultado["status"] == "error":
            raise HTTPException(status_code=404, detail=resultado)
            
        return resultado
        
    except Exception as e:
        logger.error(f"❌ Erro obter Dashboard V3: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/debug")
async def debug_dashboard_v3():
    """
    Debug Dashboard V3 - Status implementação das 4 camadas
    """
    try:
        from app.services.v3.dash_main.dash_home_service import debug_dashboard_v3
        
        return debug_dashboard_v3()
        
    except Exception as e:
        logger.error(f"❌ Erro debug Dashboard V3: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))