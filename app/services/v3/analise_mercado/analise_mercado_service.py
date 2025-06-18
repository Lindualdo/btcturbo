# app/services/v3/analise_mercado/analise_mercado_service.py
from .utils.analise_mercado import executar_analise

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def executar_analise_mercado() -> dict:
    """
    Executa análise de mercado real (Camada 1)
    """
    try:        
        return executar_analise()
        
    except Exception as e:
        logger.error(f"❌ Erro análise mercado: {str(e)}")
        # Fallback para mock em caso de erro
        return {
            "status": "error",
            "log": str(e)
        }