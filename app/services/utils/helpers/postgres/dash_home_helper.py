# app/services/utils/helpers/dashboard_home/database_helper.py

import logging
import json
from datetime import datetime
from typing import Dict, Optional
from .base import execute_query

logger = logging.getLogger(__name__)

def insert_dashboard_data(campos: dict, dashboard_json: dict) -> bool:
    """
    Insere dados consolidados no PostgreSQL
    Recebe dict com todos os campos + JSON
    """
    try:
        logger.info("💾 Inserindo dados consolidados do dashboard...")
        
        # Query dinâmica baseada nos campos disponíveis
        colunas = list(campos.keys()) + ["dashboard_json"]
        valores_placeholder = ", ".join(["%s"] * len(colunas))
        colunas_sql = ", ".join(colunas)
        
        query = f"""
            INSERT INTO dashboard_home ({colunas_sql})
            VALUES ({valores_placeholder})
        """
        
        # Preparar valores
        dashboard_json_str = json.dumps(dashboard_json)
        valores = list(campos.values()) + [dashboard_json_str]
        
        execute_query(query, tuple(valores))
        
        logger.info(f"✅ Dashboard inserido: {len(campos)} campos")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dashboard: {str(e)}")
        return False

def get_latest_dashboard() -> Optional[Dict]:
    """
    Busca último registro do dashboard
    """
    try:
        logger.info("🔍 Buscando último dashboard...")
        
        query = """
            SELECT *
            FROM dashboard_home 
            ORDER BY created_at DESC 
            LIMIT 1
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            logger.info(f"✅ Dashboard encontrado: ID {result['id']}")
            return result
        else:
            logger.warning("⚠️ Nenhum dashboard encontrado")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar dashboard: {str(e)}")
        return None