# app/services/utils/helpers/v2/dashboard_home/database_v2_helper.py

import logging
import json
from datetime import datetime
from typing import Dict, Optional
from app.services.utils.helpers.postgres.base import execute_query

logger = logging.getLogger(__name__)

def save_dashboard_v2(dashboard_data: Dict) -> bool:
    """
    Salva dashboard V2 no PostgreSQL
    """
    try:
        logger.info("💾 Salvando Dashboard V2...")
        
        _create_table_if_not_exists()
        
        campos = dashboard_data["campos"]
        dashboard_json = dashboard_data["json"]
        
        query = """
            INSERT INTO dashboard_decisao_v2 (
                btc_price, score_mercado, score_risco, ciclo_atual, 
                setup_4h, decisao_final, alavancagem_atual, health_factor,
                ema_distance, rsi_diario, dashboard_json, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        valores = (
            campos["btc_price"],
            campos["score_mercado"], 
            campos["score_risco"],
            campos["ciclo_atual"],
            campos["setup_4h"],
            campos["decisao_final"],
            campos["alavancagem_atual"],
            campos["health_factor"],
            campos["ema_distance"],
            campos["rsi_diario"],
            json.dumps(dashboard_json),
            datetime.utcnow()
        )
        
        execute_query(query, valores)
        logger.info("✅ Dashboard V2 salvo com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro salvando Dashboard V2: {str(e)}")
        return False

def get_latest_dashboard_v2() -> Optional[Dict]:
    """
    Busca último dashboard V2
    """
    try:
        logger.info("🔍 Buscando último Dashboard V2...")
        
        query = """
            SELECT * FROM dashboard_decisao_v2 
            ORDER BY created_at DESC 
            LIMIT 1
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            logger.info(f"✅ Dashboard V2 encontrado: ID {result['id']}")
            return result
        else:
            logger.warning("⚠️ Nenhum Dashboard V2 encontrado")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro buscando Dashboard V2: {str(e)}")
        return None

def _create_table_if_not_exists():
    """
    Cria tabela dashboard_decisao_v2 se não existir
    """
    try:
        query = """
            CREATE TABLE IF NOT EXISTS dashboard_decisao_v2 (
                id SERIAL PRIMARY KEY,
                btc_price DECIMAL(10,2) NOT NULL,
                score_mercado DECIMAL(5,1) NOT NULL,
                score_risco DECIMAL(5,1) NOT NULL,
                ciclo_atual VARCHAR(20) NOT NULL,
                setup_4h VARCHAR(30) NOT NULL,
                decisao_final VARCHAR(30) NOT NULL,
                alavancagem_atual DECIMAL(3,1) NOT NULL,
                health_factor DECIMAL(4,2) NOT NULL,
                ema_distance DECIMAL(6,2) NOT NULL,
                rsi_diario DECIMAL(5,1) NOT NULL,
                dashboard_json JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        
        execute_query(query)
        logger.info("✅ Tabela dashboard_decisao_v2 verificada/criada")
        
    except Exception as e:
        logger.error(f"❌ Erro criando tabela V2: {str(e)}")
        raise