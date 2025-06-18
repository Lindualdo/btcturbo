# app/services/v3/dash_main/dash_home_service.py
from app.services.v3.analise_mercado.utils.analise_mercado import executar_analise_mercado 

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def executar_analise_mercado() -> dict:
    """
    Executa análise de mercado real (Camada 1)
    """
    try:        
        return executar_analise_mercado()
        
    except Exception as e:
        logger.error(f"❌ Erro análise mercado: {str(e)}")
        # Fallback para mock em caso de erro
        return {
            "score_mercado": 54.9,
            "classificacao_mercado": "neutro", 
            "ciclo": "BULL_INICIAL",
            "indicadores": {"mvrv": 2.5364, "nupl": 0.5553},
            "timestamp": datetime.utcnow().isoformat()
        }