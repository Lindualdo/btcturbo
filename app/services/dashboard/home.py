
# app/services/utils/helpers/postgres/dashboard_home_helper.py

import logging
import json
from datetime import datetime
from typing import Dict, Optional
from .base import execute_query

logger = logging.getLogger(__name__)

def insert_dashboard_home_data(
    btc_price: float,
    position_dolar: float, 
    position_btc: float,
    alavancagem_atual: float,
    dashboard_json: dict
) -> bool:
    """
    Insere dados do dashboard home no PostgreSQL
    FASE 1: Apenas cabeçalho
    """
    try:
        logger.info(f"💾 Inserindo dashboard home:")
        logger.info(f"    BTC: ${btc_price:,.2f}")
        logger.info(f"    Posição: ${position_dolar:,.2f} ({position_btc:.6f} BTC)")
        logger.info(f"    Alavancagem: {alavancagem_atual:.2f}x")
        
        query = """
            INSERT INTO dashboard_home 
            (btc_price, position_dolar, position_btc, alavancagem_atual, dashboard_json)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        # Converter dict para JSON string
        dashboard_json_str = json.dumps(dashboard_json)
        
        params = (
            btc_price,
            position_dolar,
            position_btc, 
            alavancagem_atual,
            dashboard_json_str
        )
        
        execute_query(query, params)
        logger.info("✅ Dashboard home inserido com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dashboard home: {str(e)}")
        return False

def get_latest_dashboard_home() -> Optional[Dict]:
    """
    Busca dados mais recentes do dashboard home
    FASE 1: Retorna JSON direto para o frontend
    """
    try:
        logger.info("🔍 Buscando dados mais recentes do dashboard home...")
        
        query = """
            SELECT id, btc_price, position_dolar, position_btc, 
                   alavancagem_atual, dashboard_json, created_at
            FROM dashboard_home 
            ORDER BY created_at DESC 
            LIMIT 1
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            logger.info(f"✅ Dashboard home encontrado: ID {result['id']}, timestamp {result['created_at']}")
            return result
        else:
            logger.warning("⚠️ Nenhum dado encontrado na tabela dashboard_home")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar dashboard home: {str(e)}")
        return None



def get_dashboard_home_stats() -> Dict:
    """
    Estatísticas da tabela dashboard_home (debug/admin)
    """
    try:
        query = """
            SELECT 
                COUNT(*) as total_registros,
                MAX(created_at) as ultimo_registro,
                MIN(created_at) as primeiro_registro,
                AVG(btc_price) as btc_price_medio,
                AVG(alavancagem_atual) as alavancagem_media
            FROM dashboard_home
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            return {
                "total_registros": result["total_registros"],
                "ultimo_registro": result["ultimo_registro"],
                "primeiro_registro": result["primeiro_registro"], 
                "btc_price_medio": float(result["btc_price_medio"]) if result["btc_price_medio"] else 0,
                "alavancagem_media": float(result["alavancagem_media"]) if result["alavancagem_media"] else 0
            }
        else:
            return {"total_registros": 0}
            
    except Exception as e:
        logger.error(f"❌ Erro nas estatísticas: {str(e)}")
        return {"erro": str(e)}