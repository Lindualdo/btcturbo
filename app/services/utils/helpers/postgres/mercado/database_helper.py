#source:  app/services/utils/helpers/postgres/mercado/database_helper.py

# Busca o ciclo usando a Matriz de Ciclos de Mercado V2
# busca os indicadores e escores de Mercado no banco de dados

import logging
from datetime import datetime
from typing import Optional, Dict
from app.services.utils.helpers.postgres.base import execute_query

logger = logging.getLogger(__name__)

def get_ciclo_mercado() -> dict:
    """
    Executa análise completa de mercado (Camada 1)
    
    Returns:
        dict: Dados da análise de mercado para Dashboard V3
    """
    try:
        logger.info("📊 Executando Análise Mercado - Camada 1")
        
        # 1. Buscar indicadore e scores no banco de dados
        dados_mercado = _get_scores_indicadores_mercado () # score e indicadores
        if not dados_mercado:
            raise Exception("Nenhum dado de mercado encontrado")
        
        # 2. Extrair indicadores e scores
        score_mercado = float(dados_mercado["score_consolidado"])
        indicadores = dados_mercado["indicadores_json"]  # Já é dict
        mvrv = indicadores["ciclo"]["mvrv"]["valor"]
        nupl = indicadores["ciclo"]["nupl"]["valor"]
        
        # 3. Determinar ciclo via banco usndo a tabela matriz_ciclos_mercado V2
        ciclo_definido = _buscar_ciclo_matriz(score_mercado, mvrv, nupl)
        
        # 4. Determinar estratégia
        #estrategia_posicao = definir_estrategia_posicionamento(ciclo_definido)
        
        # 5. Retornar resultado
        resultado = {
            "timestamp": dados_mercado["timestamp"].isoformat(),
            "score_mercado": score_mercado,
            "classificacao_mercado": dados_mercado["classificacao_consolidada"],
            "ciclo": ciclo_definido["nome_ciclo"],
            "ciclo_detalhes": ciclo_definido,
            #"estrategia": estrategia_posicao,
            "indicadores": {
                "mvrv": mvrv,
                "nupl": nupl,
                "score_ciclo": float(dados_mercado["score_ciclo"]),
                "score_momentum": float(dados_mercado["score_momentum"]),
                "score_tecnico": float(dados_mercado["score_tecnico"])
            }
        }
        
        logger.info(f"✅ Mercado: {ciclo_definido['nome']} - Score {score_mercado}")
        return resultado
        
    except Exception as e:
        logger.error(f"❌ Erro análise mercado: {str(e)}")
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

def _buscar_ciclo_matriz(score: float, mvrv: float, nupl: float) -> Optional[Dict]:
    """
    Busca ciclo na matriz baseado nos indicadores
    
    Args:
        score: Score de mercado (0-100)
        mvrv: Market Value to Realized Value  
        nupl: Net Unrealized Profit/Loss
        
    Returns:
        dict: Dados do ciclo encontrado ou None
    """
    try:
        query = """
            SELECT nome_ciclo, percentual_capital, alavancagem, caracteristicas, prioridade
            FROM matriz_ciclos_mercado 
            WHERE ativo = true
              AND :score BETWEEN score_min AND score_max
              AND (:mvrv BETWEEN mvrv_min AND mvrv_max OR (mvrv_min IS NULL AND mvrv_max IS NULL))
              AND (:nupl BETWEEN nupl_min AND nupl_max OR (nupl_min IS NULL AND nupl_max IS NULL))
            ORDER BY prioridade DESC, id
            LIMIT 1
        """
        
        resultado = execute_query(query, params={
            "score": score, 
            "mvrv": mvrv, 
            "nupl": nupl
        }, fetch_one=True)
        
        if resultado:
            return {
                "nome_ciclo": resultado["nome_ciclo"],
                "percentual_capital": resultado["percentual_capital"],
                "alavancagem": float(resultado["alavancagem"]),
                "caracteristicas": resultado["caracteristicas"],
                "prioridade": resultado["prioridade"]
            }
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Erro buscar ciclo matriz: {str(e)}")
        return None