# app/services/utils/helpers/postgres/momentum_helper.py - DEBUG VERSION

import logging
from datetime import datetime
from typing import Dict, Optional
from .base import execute_query

logger = logging.getLogger(__name__)

def get_dados_momentum() -> Optional[Dict]:
    """Busca dados mais recentes do bloco momentum - DEBUG"""
    try:
        logger.info("🔍 Buscando dados do bloco MOMENTUM...")
        
        # QUERY COM DEBUG - adicionar ID para verificar qual registro está vindo
        query = """
            SELECT id, rsi_semanal, funding_rates, exchange_netflow, long_short_ratio,
                   timestamp, fonte, metadados
            FROM indicadores_momentum 
            ORDER BY id DESC 
            LIMIT 1
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            # LOG DETALHADO para debug
            logger.info(f"✅ Dados momentum encontrados:")
            logger.info(f"    ID: {result.get('id')}")
            logger.info(f"    RSI: {result.get('rsi_semanal')}")
            logger.info(f"    Funding: {result.get('funding_rates')}")
            logger.info(f"    Netflow: {result.get('exchange_netflow')}")
            logger.info(f"    L/S: {result.get('long_short_ratio')}")
            logger.info(f"    Timestamp: {result.get('timestamp')}")
            logger.info(f"    Fonte: {result.get('fonte')}")
            
            return result
        else:
            logger.warning("⚠️ Nenhum dado encontrado na tabela indicadores_momentum")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar dados do bloco momentum: {str(e)}")
        return None

def insert_dados_momentum(rsi: float, funding: float, netflow: float, ls_ratio: float, fonte: str = "Sistema") -> bool:
    """Insere novos dados no bloco momentum"""
    try:
        logger.info(f"💾 Inserindo dados momentum: RSI={rsi}, Funding={funding}, Netflow={netflow}, LS={ls_ratio}")
        
        query = """
            INSERT INTO indicadores_momentum (rsi_semanal, funding_rates, exchange_netflow, long_short_ratio, fonte, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (rsi, funding, netflow, ls_ratio, fonte, datetime.utcnow())
        
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
            SELECT id, rsi_semanal, funding_rates, exchange_netflow, long_short_ratio,
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