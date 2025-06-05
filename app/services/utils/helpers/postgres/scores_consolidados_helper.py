# app/services/utils/helpers/postgres/scores_consolidados_helper.py

import logging
from datetime import datetime, date
from typing import Dict, Optional
import json
from .base import execute_query

logger = logging.getLogger(__name__)

def get_score_cache_diario(data: date = None, incluir_risco: bool = True) -> Optional[Dict]:
    """Busca score consolidado em cache para data específica"""
    try:
        if data is None:
            data = date.today()
            
        logger.info(f"🔍 Buscando cache score para {data} - incluir_risco={incluir_risco}")
        
        query = """
            SELECT id, data, incluir_risco, score_final, classificacao_geral, 
                   kelly_allocation, acao_recomendada, pesos_dinamicos, 
                   dados_completos, timestamp, fonte
            FROM scores_consolidados 
            WHERE data = %s AND incluir_risco = %s
            ORDER BY timestamp DESC 
            LIMIT 1
        """
        
        result = execute_query(query, params=(data, incluir_risco), fetch_one=True)
        
        if result:
            logger.info(f"✅ Cache encontrado: score={result['score_final']}, timestamp={result['timestamp']}")
            return result
        else:
            logger.info("⚠️ Nenhum cache encontrado para hoje")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar cache: {str(e)}")
        return None

def save_score_cache_diario(
    score_final: float, 
    classificacao_geral: str,
    kelly_allocation: str,
    acao_recomendada: str,
    pesos_dinamicos: dict,
    dados_completos: dict,
    incluir_risco: bool = True,
    data: date = None
) -> bool:
    """Salva score consolidado no cache diário"""
    try:
        if data is None:
            data = date.today()
            
        logger.info(f"💾 Salvando cache score para {data} - score={score_final}")
        
        # Converter dicts para JSON
        pesos_json = json.dumps(pesos_dinamicos) if pesos_dinamicos else '{}'
        dados_json = json.dumps(dados_completos) if dados_completos else '{}'
        
        # INSERT com ON CONFLICT (UPSERT)
        query = """
            INSERT INTO scores_consolidados 
            (data, incluir_risco, score_final, classificacao_geral, kelly_allocation, 
             acao_recomendada, pesos_dinamicos, dados_completos, timestamp, fonte)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (data, incluir_risco) 
            DO UPDATE SET 
                score_final = EXCLUDED.score_final,
                classificacao_geral = EXCLUDED.classificacao_geral,
                kelly_allocation = EXCLUDED.kelly_allocation,
                acao_recomendada = EXCLUDED.acao_recomendada,
                pesos_dinamicos = EXCLUDED.pesos_dinamicos,
                dados_completos = EXCLUDED.dados_completos,
                timestamp = EXCLUDED.timestamp,
                fonte = EXCLUDED.fonte
        """
        
        params = (
            data, incluir_risco, score_final, classificacao_geral, 
            kelly_allocation, acao_recomendada, pesos_json, dados_json,
            datetime.utcnow(), 'Sistema'
        )
        
        execute_query(query, params)
        logger.info("✅ Cache salvo com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao salvar cache: {str(e)}")
        return False

def get_historico_scores(limit: int = 30) -> list:
    """Busca histórico de scores consolidados"""
    try:
        logger.info(f"📊 Buscando histórico scores (últimos {limit} registros)")
        
        query = """
            SELECT data, incluir_risco, score_final, classificacao_geral, 
                   kelly_allocation, timestamp
            FROM scores_consolidados 
            ORDER BY data DESC, incluir_risco DESC
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
        logger.error(f"❌ Erro ao buscar histórico: {str(e)}")
        return []

def limpar_cache_antigo(dias_manter: int = 90) -> bool:
    """Remove cache mais antigo que X dias"""
    try:
        logger.info(f"🧹 Limpando cache anterior a {dias_manter} dias")
        
        query = """
            DELETE FROM scores_consolidados 
            WHERE data < CURRENT_DATE - INTERVAL '%s days'
        """
        
        result = execute_query(query, params=(dias_manter,))
        affected = result.get('affected_rows', 0)
        
        logger.info(f"✅ {affected} registros antigos removidos")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na limpeza: {str(e)}")
        return False