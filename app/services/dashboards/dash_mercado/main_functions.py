# source: app/services/dashboards/dash_mercado/main_functions.py

import logging
from datetime import datetime
from .database_helper import save_scores_to_db, get_latest_scores_from_db

logger = logging.getLogger(__name__)

def save_dashboard_scores(dados_scores: dict) -> dict:
    """
    Salva scores consolidados no banco
    
    Args:
        dados_scores: Dict com todos os scores calculados
        
    Returns:
        dict: {"status": "success/error", "id": id_registro}
    """
    try:
        logger.info("💾 Salvando scores no banco...")
        
        resultado = save_scores_to_db(dados_scores)
        
        if resultado.get("status") == "success":
            logger.info(f"✅ Scores salvos - ID: {resultado['id']}")
            return resultado
        else:
            return {
                "status": "error",
                "erro": resultado.get("erro", "Falha ao salvar no banco")
            }
            
    except Exception as e:
        logger.error(f"❌ Erro save_dashboard_scores: {str(e)}")
        return {
            "status": "error",
            "erro": str(e)
        }

def get_latest_dashboard_scores() -> dict:
    """
    Obtém último registro de scores do banco
    
    Returns:
        dict: Dados do último registro ou None
    """
    try:
        return get_latest_scores_from_db()
        
    except Exception as e:
        logger.error(f"❌ Erro get_latest_dashboard_scores: {str(e)}")
        return None