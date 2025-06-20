# app/services/utils/helpers/postgres/ciclo_helper.py - v5.1.2 SIMPLIFICADO

import logging
from datetime import datetime
from typing import Dict, Optional
from ..base import execute_query

logger = logging.getLogger(__name__)

def get_dados_ciclo() -> Optional[Dict]:
    """Busca dados mais recentes do bloco ciclo"""
    try:
        logger.info("🔍 Buscando dados do bloco CICLO...")
        
        query = """
            SELECT mvrv_z_score, realized_ratio, puell_multiple, nupl,
                   timestamp, fonte, metadados
            FROM indicadores_ciclo 
            ORDER BY timestamp DESC 
            LIMIT 1
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            logger.info(f"✅ Dados ciclo encontrados: timestamp={result['timestamp']}")
            return result
        else:
            logger.warning("⚠️ Nenhum dado encontrado na tabela indicadores_ciclo")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar dados do bloco ciclo: {str(e)}")
        return None

def insert_dados_ciclo(
    mvrv_z: float, 
    realized_ratio: float, 
    puell_multiple: float, 
    nupl: float = None,
    fonte: str = "Sistema"
) -> bool:
    """Insere novos dados no bloco ciclo"""
    try:
        logger.info(f"💾 Inserindo dados ciclo: MVRV={mvrv_z}, Realized={realized_ratio}, Puell={puell_multiple}, NUPL={nupl}")
        
        query = """
            INSERT INTO indicadores_ciclo 
            (mvrv_z_score, realized_ratio, puell_multiple, nupl, fonte, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        params = (mvrv_z, realized_ratio, puell_multiple, nupl, fonte, datetime.utcnow())
        
        execute_query(query, params)
        logger.info("✅ Dados ciclo inseridos com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dados ciclo: {str(e)}")
        return False

def get_historico_ciclo(limit: int = 10) -> list:
    """Busca histórico de dados do bloco ciclo"""
    try:
        logger.info(f"📊 Buscando histórico do bloco CICLO (últimos {limit} registros)")
        
        query = """
            SELECT mvrv_z_score, realized_ratio, puell_multiple, nupl,
                   timestamp, fonte
            FROM indicadores_ciclo 
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
        logger.error(f"❌ Erro ao buscar histórico ciclo: {str(e)}")
        return []

def insert_dados_ciclo_legacy(mvrv_z: float, realized_ratio: float, puell_multiple: float, fonte: str = "Sistema") -> bool:
    """COMPATIBILIDADE: Função legada sem NUPL"""
    logger.warning("⚠️ Usando função legada insert_dados_ciclo_legacy")
    return insert_dados_ciclo(
        mvrv_z=mvrv_z,
        realized_ratio=realized_ratio, 
        puell_multiple=puell_multiple,
        nupl=None,
        fonte=fonte
    )