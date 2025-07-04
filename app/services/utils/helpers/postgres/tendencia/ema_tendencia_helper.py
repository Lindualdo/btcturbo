# app/services/utils/helpers/postgres/indicadores/emas_tendencia_helper.py

import json
import logging
from datetime import datetime
from typing import Dict, Optional
from app.services.utils.helpers.postgres.base import execute_query

logger = logging.getLogger(__name__)

def inserir(dados: Dict) -> bool:
    """Insere dados tendencia"""
    try:
        logger.info("💾 Inserindo emas tendencia...")
        
        query = """
            INSERT INTO score_tendencia (emas_json, score_emas, classificacao_emas, timestamp) 
            VALUES (%s, %s, %s, %s)
        """
        
        params = (
            dados.get("emas_json"), dados.get("score_emas"), dados.get("classificacao_emas"), datetime.utcnow()
        )
        
        execute_query(query, params)
        logger.info("✅ Emas tendencia inseridos com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir emas tendencia: {str(e)}")
        return False

def obter() -> Optional[Dict]:
    """Busca dados score tendencia mais recentes"""
    try:
        logger.info("🔍 Buscando score tendencia...")
        
        query = """
            SELECT 
                emas_json, score_emas, classificacao_emas, timestamp
            FROM score_tendencia 
            ORDER BY timestamp DESC 
            LIMIT 1
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            logger.info(f"✅ Dados encontrados: score={result.get('score_emas')}")
            return result
        else:
            logger.warning("⚠️ Nenhum dado encontrado")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar dados: {str(e)}")
        return None