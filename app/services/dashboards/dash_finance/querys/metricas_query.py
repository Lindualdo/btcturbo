# app/services/dashboards/dash_finance/health_factor_query.py

import logging
from app.services.utils.helpers.postgres.base import execute_query

logger = logging.getLogger(__name__)

def get_metricas_atual() -> list:
    """
    Query Metricas - último registro do dash-main
    """
    try:
        query = """
            SELECT id, 
	        health_factor,
	        alavancagem_atual,
	        score_risco
	    FROM 
	        public.dash_main
        order by id desc
	    limit 1;
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            logger.info(f"✅ Dados ciclo encontrados: timestamp={result['timestamp']}")
            return result
        else:
            logger.warning("⚠️ Nenhum dado encontrado na tabela indicadores_ciclo")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro query Health Factor: {str(e)}")
        return []