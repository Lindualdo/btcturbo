#source: app/services/dashboards/dash_main/analise_mercado/database_helper.py

import logging
from datetime import datetime
from app.services.utils.helpers.postgres.base import execute_query

logger = logging.getLogger(__name__)
def get_latest_scores_from_db() -> dict:
    """
    Obtém último registro com JSON já formatado
    """
    try:
        query = """
            SELECT 
                id, timestamp,
                score_ciclo, classificacao_ciclo,
                score_momentum, classificacao_momentum,
                score_tecnico, classificacao_tecnico, 
                score_consolidado, classificacao_consolidada,
                indicadores_json
            FROM dashboard_mercado_scores
            ORDER BY timestamp DESC
            LIMIT 1
        """
        
        resultado = execute_query(query, fetch_one=True)
        
        if resultado:
            logger.info(f"✅ Último registro obtido - ID: {resultado['id']}")
            return resultado
        else:
            logger.info("ℹ️ Nenhum registro encontrado")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro get_latest_scores_from_db: {str(e)}")
        return None