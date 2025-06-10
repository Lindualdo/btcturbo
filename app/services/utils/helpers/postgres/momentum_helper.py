# app/services/utils/helpers/postgres/momentum_helper.py - v5.1.3 COM SOPR

import logging
from datetime import datetime
from typing import Dict, Optional
from .base import execute_query

logger = logging.getLogger(__name__)

def get_dados_momentum() -> Optional[Dict]:
    """Busca dados mais recentes do bloco momentum - v5.1.3 COM SOPR"""
    try:
        logger.info("🔍 Buscando dados do bloco MOMENTUM v5.1.3...")
        
        # QUERY ATUALIZADA v5.1.3 - incluindo SOPR
        query = """
            SELECT id, rsi_semanal, funding_rates, exchange_netflow, long_short_ratio,
                   sopr, timestamp, fonte, metadados
            FROM indicadores_momentum 
            ORDER BY id DESC 
            LIMIT 1
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            # LOG DETALHADO para v5.1.3
            logger.info(f"✅ Dados momentum v5.1.3 encontrados:")
            logger.info(f"    ID: {result.get('id')}")
            logger.info(f"    RSI: {result.get('rsi_semanal')}")
            logger.info(f"    Funding: {result.get('funding_rates')}")
            logger.info(f"    Exchange Netflow: {result.get('exchange_netflow')} (compatibilidade)")
            logger.info(f"    SOPR: {result.get('sopr')} ← NOVO v5.1.3")
            logger.info(f"    L/S: {result.get('long_short_ratio')}")
            logger.info(f"    Timestamp: {result.get('timestamp')}")
            
            return result
        else:
            logger.warning("⚠️ Nenhum dado encontrado na tabela indicadores_momentum")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar dados do bloco momentum v5.1.3: {str(e)}")
        return None

def insert_dados_momentum(
    rsi: float, 
    funding: float, 
    netflow: float, 
    ls_ratio: float, 
    sopr: float = None,  # ← NOVO v5.1.3
    fonte: str = "Sistema"
) -> bool:
    """
    Insere novos dados no bloco momentum - v5.1.3 COM SOPR
    
    Args:
        rsi: RSI Semanal
        funding: Funding Rates
        netflow: Exchange Netflow (mantido para compatibilidade)
        ls_ratio: Long/Short Ratio
        sopr: SOPR - Spent Output Profit Ratio (NOVO v5.1.3)
        fonte: Fonte dos dados
    
    Returns:
        bool: Sucesso da operação
    """
    try:
        logger.info(f"💾 Inserindo dados momentum v5.1.3:")
        logger.info(f"    RSI={rsi}, Funding={funding}")
        logger.info(f"    Netflow={netflow} (compatibilidade), L/S={ls_ratio}")
        logger.info(f"    SOPR={sopr} ← NOVO v5.1.3")
        
        # QUERY ATUALIZADA v5.1.3 - incluindo SOPR
        query = """
            INSERT INTO indicadores_momentum 
            (rsi_semanal, funding_rates, exchange_netflow, long_short_ratio, sopr, fonte, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (rsi, funding, netflow, ls_ratio, sopr, fonte, datetime.utcnow())
        
        execute_query(query, params)
        logger.info("✅ Dados momentum v5.1.3 inseridos com sucesso (incluindo SOPR)")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dados momentum v5.1.3: {str(e)}")
        return False