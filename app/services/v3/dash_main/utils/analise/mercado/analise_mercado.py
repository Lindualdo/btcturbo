# app/services/v3/dash_main/utils/analise/mercado/analise_mercado.py

import logging
import json
from datetime import datetime
from .matriz_ciclos import identificar_ciclo
from .estrategia_posicionamento import definir_estrategia

logger = logging.getLogger(__name__)

def executar_analise_mercado() -> dict:
    """
    Executa análise completa de mercado (Camada 1)
    
    Fluxo:
    1. Busca dados consolidados (database_helper)
    2. Identifica ciclo (matriz_ciclos) 
    3. Define estratégia (estrategia_posicionamento)
    4. Retorna dados para Dashboard V3
    """
    try:
        logger.info("📊 Executando Análise Mercado - Camada 1")
        
        # 1. Buscar dados consolidados
        dados_mercado = _get_dados_mercado_consolidados()
        
        if not dados_mercado:
            raise Exception("Dados de mercado indisponíveis")
        
        # 2. Extrair indicadores chave
        score_mercado_raw = float(dados_mercado["score_consolidado"])
        # CORREÇÃO: Score no banco está base 10, matriz usa base 100
        score_mercado = score_mercado_raw * 10
        
        # Verificar se indicadores_json é string ou dict
        indicadores_json = dados_mercado["indicadores_json"]
        if isinstance(indicadores_json, str):
            indicadores = json.loads(indicadores_json)
        else:
            indicadores = indicadores_json
        
        mvrv = indicadores["ciclo"]["mvrv"]["valor"]
        nupl = indicadores["ciclo"]["nupl"]["valor"]
        
        # 3. Identificar ciclo usando matriz
        ciclo_identificado = identificar_ciclo(score_mercado, mvrv, nupl)
        
        # 4. Definir estratégia de posicionamento
        estrategia = definir_estrategia(ciclo_identificado)
        
        # 5. Retornar dados formatados
        resultado = {
            "timestamp": dados_mercado["timestamp"].isoformat(),
            "score_mercado": score_mercado,
            "classificacao_mercado": dados_mercado["classificacao_consolidada"],
            "ciclo": ciclo_identificado["nome"],
            "ciclo_detalhes": ciclo_identificado,
            "estrategia": estrategia,
            "indicadores": {
                "mvrv": mvrv,
                "nupl": nupl,
                "score_ciclo": float(dados_mercado["score_ciclo"]),
                "score_momentum": float(dados_mercado["score_momentum"]),
                "score_tecnico": float(dados_mercado["score_tecnico"])
            }
        }
        
        logger.info(f"✅ Mercado: {ciclo_identificado['nome']} - Score {score_mercado_raw}→{score_mercado}")
        return resultado
        
    except Exception as e:
        logger.error(f"❌ Erro análise mercado: {str(e)}")
        raise Exception(f"Falha na análise de mercado: {str(e)}")

def _get_dados_mercado_consolidados() -> dict:
    """
    Busca dados consolidados usando database_helper existente
    """
    try:
        from app.services.v3.dash_mercado.utils.database_helper import get_latest_scores_from_db
        
        dados = get_latest_scores_from_db()
        
        if dados:
            logger.info(f"✅ Dados mercado obtidos - ID: {dados['id']}")
            return dados
        else:
            logger.warning("⚠️ Nenhum dado consolidado encontrado")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro buscar dados: {str(e)}")
        return None