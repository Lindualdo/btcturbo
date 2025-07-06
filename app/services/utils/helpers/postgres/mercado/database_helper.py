#source:  app/services/utils/helpers/postgres/mercado/database_helper.py

import logging
from datetime import datetime
from typing import Optional, Dict
from app.services.utils.helpers.postgres.base import execute_query

logger = logging.getLogger(__name__)

def get_ciclo_mercado() -> dict:
    try:
        logger.info("📊 Executando Análise Mercado - Camada 1")
        
        # 1. Buscar dados de mercado
        dados_mercado = _get_scores_indicadores_mercado() # score e indicadores

        if not dados_mercado:
            raise Exception("Nenhum dado de mercado encontrado")
        
        # 2. Extrair indicadores e scores
        score_mercado = float(dados_mercado["score_consolidado"])
       
        # Descontinuado na v1.8 / será usado matriz da camada de tendencia
        ciclo_definido = _buscar_dados_estrategicos(score_mercado) 
        
        # 4. Fallback se não encontrar ciclo
        if not ciclo_definido:
            alert = f"⚠️ Ciclo não encontrado para Score:{score_mercado}"
            logger.warning(alert)
            ciclo_definido = {
                "nome_ciclo": "CICLO INDEFINIDO",
                "percentual_capital": 0,
                "alavancagem": 1.0,
                "caracteristicas": f"Gap na matriz - {alert}",
                "prioridade": 0
            }
        
        # 5. Retornar resultado
        resultado = {
            "timestamp": dados_mercado["timestamp"].isoformat(),
            "score_mercado": score_mercado,
            "classificacao_mercado": dados_mercado["classificacao_consolidada"],
            "ciclo_name": ciclo_definido["nome_ciclo"],
            "ciclo_detail": ciclo_definido["caracteristicas"],
            "ciclo_detalhes": ciclo_definido,
            "indicadores": {
                "score_ciclo": float(dados_mercado["score_ciclo"]),
                "score_momentum": float(dados_mercado["score_momentum"]),
                "score_tecnico": float(dados_mercado["score_tecnico"])
            }
        }
        
        logger.info(f"✅ Mercado: {ciclo_definido['nome_ciclo']} - Score {score_mercado}")
        return resultado
        
    except Exception as e:
        logger.error(f"❌ Erro análise mercado: {str(e)}")
        logger.error(f"Score: {score_mercado if 'score_mercado' in locals() else 'N/A'}, MVRV: {mvrv if 'mvrv' in locals() else 'N/A'}, NUPL: {nupl if 'nupl' in locals() else 'N/A'}")
        raise Exception(f"Falha na análise de mercado: {str(e)}")


def _get_scores_indicadores_mercado() -> dict:
    """
    Obtém último registro com JSON já formatado
    """
    try:
        query = """
            SELECT 
                id, timestamp,
                score_ciclo, classificacao_ciclo,
                score_momentum, classificacao_momentum,
                score_tecnico, classificacao_tecnico, 
                score_consolidado, classificacao_consolidada,
                indicadores_json
            FROM dash_mercado
            ORDER BY timestamp DESC
            LIMIT 1
        """
        
        resultado = execute_query(query, fetch_one=True)
        
        if resultado:
            logger.info(f"✅ Último registro obtido - ID: {resultado['id']}")
            return resultado
        else:
            logger.info("ℹ️ Nenhum registro encontrado")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro get_latest_scores_from_db: {str(e)}")
        return None
    
def _buscar_dados_estrategicos(score: float) -> Optional[Dict]:
    """
    Busca dados estratégicos usando a última decisão estratégica processada
    
    Args:
        score: Score consolidado de mercado (0-100) - não usado, mantido para compatibilidade
        
    Returns:
        Dict com dados estratégicos ou None
    """
    try:
        logger.info(f"🔍 Buscando dados estratégicos da última decisão")
        
        from app.services.decisao_estrategica.utils.data_helper import get_detalhe_estrategia
        
        ultima_decisao = get_detalhe_estrategia()
        
        if ultima_decisao:
            # Mapear para formato esperado mantendo compatibilidade
            dados_estrategicos = {
                "nome_ciclo": ultima_decisao["fase_operacional"],
                "percentual_capital": int(ultima_decisao["satelite"] * 100),  # converter decimal para %
                "alavancagem": float(ultima_decisao["alavancagem"]),
                "caracteristicas": ultima_decisao["acao"],
                "prioridade": 1  # Prioridade fixa para última decisão
            }
            
            logger.info(f"✅ Estratégia encontrada: {dados_estrategicos['nome_ciclo']} - Alavancagem {dados_estrategicos['alavancagem']}x")
            return dados_estrategicos
        else:
            logger.warning("⚠️ Nenhuma decisão estratégica encontrada")
            return None
        
    except Exception as e:
        logger.error(f"❌ Erro buscar dados estratégicos: {str(e)}")
        return None