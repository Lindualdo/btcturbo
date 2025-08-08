# app/services/dashboards/dash_finance/patrimonio_query.py

import logging
from app.services.utils.helpers.postgres.base import execute_query

logger = logging.getLogger(__name__)

def get_patrimonio_data(data_inicio) -> list:
    """
    Query Patrimônio Líquido + BTC Price - último registro de cada dia
    """
    try:
        query = """
            SELECT 
                DATE(timestamp) as data,
                timestamp,
                net_asset_value as valor,
                btc_price,
                saldo_btc_core
            FROM indicadores_risco r1
            WHERE timestamp >= %s
              AND net_asset_value IS NOT NULL
              AND id > 16
              AND timestamp = (
                SELECT MAX(timestamp) 
                FROM indicadores_risco r2 
                WHERE DATE(r1.timestamp) = DATE(r2.timestamp)
                  AND net_asset_value IS NOT NULL
              )
            ORDER BY timestamp DESC;
        """
        
        resultados = execute_query(query, params=(data_inicio,), fetch_all=True)
        
        if resultados:
            dados = [
                {
                    "timestamp": row["timestamp"].isoformat(),
                    "valor": float(row["valor"]) if row["valor"] else 0.0,
                    "btc_price": float(row["btc_price"]) if row["btc_price"] else 0.0,
                    "saldo_btc_core": float(row["saldo_btc_core"]) if row["saldo_btc_core"] else 0.0
                }
                for row in resultados
            ]
            logger.info(f"✅ Patrimônio: {len(dados)} registros obtidos")
            return dados
        else:
            logger.warning("⚠️ Nenhum registro Patrimônio encontrado")
            return []
            
    except Exception as e:
        logger.error(f"❌ Erro query Patrimônio: {str(e)}")
        return []