# app/services/utils/helpers/postgres/indicadores/tecnico_v3_helper.py

import json
import logging
from datetime import datetime
from typing import Dict, Optional
from app.services.utils.helpers.postgres.base import execute_query

logger = logging.getLogger(__name__)

def insert_dados_tecnico(dados: Dict) -> bool:
    """Insere dados técnico v3.0"""
    try:
        logger.info("💾 Inserindo dados técnico...")
        
        distancias_json_str = json.dumps(dados.get("distancias_emas_json", {}))
        
        query = """
            INSERT INTO indicadores_tecnico (
                ema_17_1w, ema_34_1w, ema_144_1w, ema_305_1w, ema_610_1w,
                ema_17_1d, ema_34_1d, ema_144_1d, ema_305_1d, ema_610_1d,
                btc_price_current, score_consolidado_1w, score_consolidado_1d, score_final_ponderado, timestamp
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, 
            )
        """
        
        params = (
            dados.get("ema_17_1w"), dados.get("ema_34_1w"), dados.get("ema_144_1w"),dados.get("ema_305_1w"), dados.get("ema_610_1w"),
            dados.get("ema_17_1d"), dados.get("ema_34_1d"), dados.get("ema_144_1d"),dados.get("ema_305_1d"), dados.get("ema_610_1d"),
            dados.get("btc_price_current"), dados.get("score_consolidado_1w"), dados.get("score_consolidado_1d"), dados.get("score_final_ponderado"), dados.get("timestamp", datetime.utcnow())
        )
        
        execute_query(query, params)
        logger.info("✅ Dados técnico inseridos com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dados técnico: {str(e)}")
        return False

def get_dados_tecnico() -> Optional[Dict]:
    """Busca dados técnicos mais recentes"""
    try:
        logger.info("🔍 Buscando dados técnico...")
        
        query = """
            SELECT 
                ema_17_1w, ema_34_1w, ema_144_1w, ema_305_1w, ema_610_1w,
                ema_17_1d, ema_34_1d, ema_144_1d, ema_305_1d, ema_610_1d,
                btc_price_current,
                score_consolidado_1w, score_consolidado_1d, score_final_ponderado
            FROM indicadores_tecnico 
            ORDER BY timestamp DESC 
            LIMIT 1
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            logger.info(f"✅ Dados encontrados: score={result.get('score_final_ponderado')}")
            return result
        else:
            logger.warning("⚠️ Nenhum dado encontrado")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar dados: {str(e)}")
        return None