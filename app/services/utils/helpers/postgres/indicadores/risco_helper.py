# app/services/utils/helpers/postgres/risco_helper.py

import logging
from datetime import datetime
from typing import Dict, Optional
from ..base import execute_query

logger = logging.getLogger(__name__)

def get_dados_risco() -> Optional[Dict]:
    """Busca dados mais recentes do bloco risco"""
    try:
        logger.info("🔍 Buscando dados do bloco RISCO...")
        
        query = """
            SELECT dist_liquidacao, health_factor,
                   btc_price, total_borrowed, supplied_asset_value, net_asset_value, alavancagem,
                   timestamp, fonte, metadados
            FROM indicadores_risco 
            ORDER BY timestamp DESC 
            LIMIT 1
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            logger.info(f"✅ Dados risco encontrados: HF={result.get('health_factor')}, timestamp={result['timestamp']}")
            return result
        else:
            logger.warning("⚠️ Nenhum dado encontrado na tabela indicadores_risco")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar dados do bloco risco: {str(e)}")
        return None

def insert_dados_risco_completo(
    dist_liquidacao: float,
    health_factor: float, 
    btc_price: float,
    total_borrowed: float,
    supplied_asset_value: float,
    net_asset_value: float,
    alavancagem: float,
    liquidation_price: float,
    fonte: str = "aave/web3"
) -> bool:
    """Insere dados completos do bloco risco"""
    try:
        logger.info(f"💾 Inserindo dados risco completos: HF={health_factor:.2f}, Dist={dist_liquidacao:.1f}%")
        
        query = """
            INSERT INTO indicadores_risco 
            (dist_liquidacao, health_factor, btc_price, total_borrowed, supplied_asset_value, 
             net_asset_value, alavancagem, liquidation_price, fonte, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            dist_liquidacao, health_factor, btc_price, total_borrowed, 
            supplied_asset_value, net_asset_value, alavancagem, liquidation_price, fonte, datetime.utcnow()
        )
        
        execute_query(query, params)
        logger.info("✅ Dados risco completos inseridos com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dados risco: {str(e)}")
        return False

def get_historico_risco(limit: int = 10) -> list:
    """Busca histórico de dados do bloco risco"""
    try:
        logger.info(f"📊 Buscando histórico do bloco RISCO (últimos {limit} registros)")
        
        query = """
            SELECT dist_liquidacao, health_factor, btc_price, total_borrowed, 
                   supplied_asset_value, net_asset_value, alavancagem,
                   timestamp, fonte
            FROM indicadores_risco 
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
        logger.error(f"❌ Erro ao buscar histórico risco: {str(e)}")
        return []