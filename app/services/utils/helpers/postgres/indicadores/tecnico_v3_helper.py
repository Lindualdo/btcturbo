# app/services/utils/helpers/postgres/indicadores/tecnico_v3_helper.py - VERSÃO SIMPLIFICADA

import logging
from datetime import datetime
from typing import Dict
from app.services.utils.helpers.postgres.base import execute_query

logger = logging.getLogger(__name__)

def insert_dados_tecnico(dados: Dict) -> bool:
    """
    Insere dados técnico v3.0 - VERSÃO SIMPLIFICADA
    Apenas EMAs + Scores principais + Metadados básicos
    """
    try:
        logger.info("💾 Inserindo dados técnico SIMPLIFICADO...")
        
        # Query simplificada - apenas campos essenciais
        query = """
            INSERT INTO indicadores_tecnico (
                ema_17_1w, ema_34_1w, ema_144_1w, ema_305_1w, ema_610_1w,
                ema_17_1d, ema_34_1d, ema_144_1d, ema_305_1d, ema_610_1d,
                btc_price_current,
                score_consolidado_1w, score_consolidado_1d, score_final_ponderado,
                fonte, timestamp
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s,
                %s, %s, %s,
                %s, %s
            )
        """
        
        # Params organizados - apenas campos essenciais
        params = (
            # EMAs Semanal (5)
            dados.get("ema_17_1w"),
            dados.get("ema_34_1w"),
            dados.get("ema_144_1w"),
            dados.get("ema_305_1w"),
            dados.get("ema_610_1w"),
            
            # EMAs Diário (5)
            dados.get("ema_17_1d"),
            dados.get("ema_34_1d"),
            dados.get("ema_144_1d"),
            dados.get("ema_305_1d"),
            dados.get("ema_610_1d"),
            
            # Preço atual (1)
            dados.get("btc_price_current"),
            
            # Scores principais (3)
            dados.get("score_consolidado_1w"),
            dados.get("score_consolidado_1d"),
            dados.get("score_final_ponderado"),
            
            # Metadados (2)
            dados.get("fonte", "tecnico_v3"),
            dados.get("timestamp", datetime.utcnow())
        )
        
        execute_query(query, params)
        logger.info("✅ Dados técnico SIMPLIFICADO inseridos com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dados técnico SIMPLIFICADO: {str(e)}")
        return False

def get_dados_tecnico() -> dict:
    """
    Busca dados técnico v3.0 - VERSÃO SIMPLIFICADA
    """
    try:
        logger.info("🔍 Buscando dados técnico SIMPLIFICADO...")
        
        query = """
            SELECT 
                ema_17_1w, ema_34_1w, ema_144_1w, ema_305_1w, ema_610_1w,
                ema_17_1d, ema_34_1d, ema_144_1d, ema_305_1d, ema_610_1d,
                btc_price_current,
                score_consolidado_1w, score_consolidado_1d, score_final_ponderado,
                fonte, timestamp
            FROM indicadores_tecnico 
            ORDER BY timestamp DESC 
            LIMIT 1
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            logger.info(f"✅ Dados técnico encontrados: score_final={result.get('score_final_ponderado')}")
            return result
        else:
            logger.warning("⚠️ Nenhum dado técnico encontrado")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar dados técnico: {str(e)}")
        return None