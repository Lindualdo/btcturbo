# app/services/utils/helpers/postgres/momentum_helper.py

import logging
from datetime import datetime
from typing import Dict, Optional
from .base import execute_query

logger = logging.getLogger(__name__)

def get_dados_momentum() -> Optional[Dict]:
    """Busca dados mais recentes do bloco momentum"""
    try:
        logger.info("🔍 Buscando dados do bloco MOMENTUM...")
        
        query = """
            SELECT rsi_semanal, funding_rates, oi_change, long_short_ratio,
                   timestamp, fonte, metadados
            FROM indicadores_momentum 
            ORDER BY timestamp DESC 
            LIMIT 1
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            logger.info(f"✅ Dados momentum encontrados: timestamp={result['timestamp']}")
            return result
        else:
            logger.warning("⚠️ Nenhum dado encontrado na tabela indicadores_momentum")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar dados do bloco momentum: {str(e)}")
        return None

def insert_dados_momentum(rsi: float, funding: float, oi_change: float, ls_ratio: float, fonte: str = "Sistema") -> bool:
    """Insere novos dados no bloco momentum"""
    try:
        logger.info(f"💾 Inserindo dados momentum: RSI={rsi}, Funding={funding}, OI={oi_change}, LS={ls_ratio}")
        
        query = """
            INSERT INTO indicadores_momentum (rsi_semanal, funding_rates, oi_change, long_short_ratio, fonte, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (rsi, funding, oi_change, ls_ratio, fonte, datetime.utcnow())
        
        execute_query(query, params)
        logger.info("✅ Dados momentum inseridos com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dados momentum: {str(e)}")
        return False

def get_historico_momentum(limit: int = 10) -> list:
    """Busca histórico de dados do bloco momentum"""
    try:
        logger.info(f"📊 Buscando histórico do bloco MOMENTUM (últimos {limit} registros)")
        
        query = """
            SELECT rsi_semanal, funding_rates, oi_change, long_short_ratio,
                   timestamp, fonte
            FROM indicadores_momentum 
            ORDER BY timestamp DESC 
            LIMIT %s
        """
        
        result = execute_query(query, params=(limit,), fetch_all=True)
        
        if result:
            logger.info(f"✅ {len(result)} registros históricos encontrados")
            return result
        else:
            logger.warning("⚠️ Nenhum histórico encontrado")
            return []
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar histórico momentum: {str(e)}")
        return []