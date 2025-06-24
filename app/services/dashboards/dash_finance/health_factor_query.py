# app/services/dashboards/dash_finance/queries/health_factor_query.py

import logging
from app.services.utils.helpers.postgres.base import execute_query

logger = logging.getLogger(__name__)

def get_health_factor_data(data_inicio) -> list:
    """
    Query Health Factor - último registro de cada dia
    """
    try:
        query = """
            SELECT 
                DATE(timestamp) as data,
                timestamp,
                health_factor as valor
            FROM indicadores_risco r1
            WHERE timestamp >= %s
              AND health_factor IS NOT NULL
              AND timestamp = (
                SELECT MAX(timestamp) 
                FROM indicadores_risco r2 
                WHERE DATE(r1.timestamp) = DATE(r2.timestamp)
                  AND health_factor IS NOT NULL
              )
            ORDER BY timestamp DESC;
        """
        
        resultados = execute_query(query, params=(data_inicio,), fetch_all=True)
        
        if resultados:
            dados = [
                {
                    "timestamp": row["timestamp"].isoformat(),
                    "valor": float(row["valor"]) if row["valor"] else 0.0
                }
                for row in resultados
            ]
            logger.info(f"✅ Health Factor: {len(dados)} registros obtidos")
            return dados
        else:
            logger.warning("⚠️ Nenhum registro Health Factor encontrado")
            return []
            
    except Exception as e:
        logger.error(f"❌ Erro query Health Factor: {str(e)}")
        return []