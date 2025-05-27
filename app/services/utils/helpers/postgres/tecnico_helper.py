# app/services/utils/helpers/postgres/tecnico_helper.py

import logging
from datetime import datetime
from typing import Dict, Optional
from .base import execute_query

logger = logging.getLogger(__name__)

def get_dados_tecnico() -> Optional[Dict]:
    """Busca dados mais recentes do bloco técnico"""
    try:
        logger.info("🔍 Buscando dados do bloco TÉCNICO...")
        
        query = """
            SELECT sistema_emas, padroes_graficos,
                   timestamp, fonte, metadados
            FROM indicadores_tecnico 
            ORDER BY timestamp DESC 
            LIMIT 1
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            logger.info(f"✅ Dados técnico encontrados: timestamp={result['timestamp']}")
            return result
        else:
            logger.warning("⚠️ Nenhum dado encontrado na tabela indicadores_tecnico")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar dados do bloco técnico: {str(e)}")
        return None

def insert_dados_tecnico(sistema_emas: float, padroes: float, fonte: str = "Sistema") -> bool:
    """Insere novos dados no bloco técnico"""
    try:
        logger.info(f"💾 Inserindo dados técnico: EMAs={sistema_emas}, Padrões={padroes}")
        
        query = """
            INSERT INTO indicadores_tecnico (sistema_emas, padroes_graficos, fonte, timestamp)
            VALUES (%s, %s, %s, %s)
        """
        params = (sistema_emas, padroes, fonte, datetime.utcnow())
        
        execute_query(query, params)
        logger.info("✅ Dados técnico inseridos com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dados técnico: {str(e)}")
        return False

def get_historico_tecnico(limit: int = 10) -> list:
    """Busca histórico de dados do bloco técnico"""
    try:
        logger.info(f"📊 Buscando histórico do bloco TÉCNICO (últimos {limit} registros)")
        

        query = """
            SELECT sistema_emas, padroes_graficos,
                   timestamp, fonte 
            FROM indicadores_tecnico 
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
        logger.error(f"❌ Erro ao buscar histórico técnico: {str(e)}")
        return []