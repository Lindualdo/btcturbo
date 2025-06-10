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
    score_mercado: float,
    score_mercado_classificacao: str,
    mvrv_valor: float,
    nupl_valor: float,
    dashboard_json: dict
) -> bool:
    """Insere dados do dashboard home no PostgreSQL"""
    try:
        logger.info(f"💾 Inserindo dashboard home: BTC=${btc_price:,.2f}, Posição=${position_dolar:,.2f}")
        
        query = """
            INSERT INTO dashboard_home 
            (btc_price, position_dolar, position_btc, alavancagem_atual,
             score_mercado, score_mercado_classificacao, mvrv_valor, nupl_valor, dashboard_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        dashboard_json_str = json.dumps(dashboard_json)
        params = (
            btc_price, position_dolar, position_btc, alavancagem_atual,
            score_mercado, score_mercado_classificacao, mvrv_valor, nupl_valor, dashboard_json_str
        )
        
        execute_query(query, params)
        logger.info("✅ Dashboard home inserido com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dashboard home: {str(e)}")
        return False

def get_latest_dashboard_home() -> Optional[Dict]:
    """Busca dados mais recentes do dashboard home"""
    try:
        logger.info("🔍 Buscando dados mais recentes do dashboard home...")
        
        query = """
            SELECT id, btc_price, position_dolar, position_btc, alavancagem_atual,
                   score_mercado, score_mercado_classificacao, mvrv_valor, nupl_valor,
                   dashboard_json, created_at
            FROM dashboard_home 
            ORDER BY created_at DESC 
            LIMIT 1
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            logger.info(f"✅ Dashboard home encontrado: ID {result['id']}")
            return result
        else:
            logger.warning("⚠️ Nenhum dado encontrado na tabela dashboard_home")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar dashboard home: {str(e)}")
        return None