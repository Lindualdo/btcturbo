#router: app.routers.v3.analise_mercado

from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging


logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/analise-mercado")
async def analise_mercado():
    """
    Camada 1 - Análise de Mercado
    Retorna dados brutos + ciclo identificado + estratégia
    """
    try:
        from app.services.v3.analise_mercado.analise_mercado_service import executar_analise_mercado
        resultado = executar_analise_mercado()
        
        return {
            "status": "success",
            "camada": "1-mercado",
            "dados": resultado
        }
        
    except Exception as e:
        logger.error(f"❌ Erro debug mercado: {str(e)}")
        return {
            "status": "error",
            "camada": "1-mercado", 
            "erro": str(e)
        }