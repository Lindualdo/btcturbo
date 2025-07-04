# app/services/decisao_estrategica/estrategia_service.py

import logging
from datetime import datetime
from typing import Dict, Optional
from app.services.utils.helpers.postgres.tendencia.ema_tendencia_helper import obter as obter_score_tendencia
from app.services.scores.ciclos import calcular_score as calcular_score_ciclo
from app.services.utils.helpers.postgres.estrategia.estrategia_helper import (
    obter_estrategia, inserir_decisao, get_ultima_decisao, validar_matriz_completa
)

logger = logging.getLogger(__name__)

def processar_decisao_estrategica() -> Dict:
    """
    Processa decisão estratégica completa:
    1. Busca scores (tendência + ciclo)
    2. Consulta matriz estratégica  
    3. Aplica decisão
    4. Grava histórico
    
    Returns:
        Dict com decisão estratégica aplicada
    """
    try:
        logger.info("🚀 Processando Decisão Estratégica...")
        
        # 1. BUSCAR SCORES
        scores_data = _buscar_scores()
        if not scores_data:
            raise Exception("Falha ao obter scores necessários")
        
        score_tendencia = scores_data["score_tendencia"]
        score_ciclo = scores_data["score_ciclo"]
        
        logger.info(f"📊 Scores obtidos: Tendência={score_tendencia}, Ciclo={score_ciclo}")
        
        # 2. CONSULTAR MATRIZ ESTRATÉGICA
        estrategia = obter_estrategia(score_tendencia, score_ciclo)
        if not estrategia:
            raise Exception(f"Nenhuma estratégia encontrada para scores T:{score_tendencia}, C:{score_ciclo}")
        
        logger.info(f"🎯 Estratégia identificada: {estrategia['fase_operacional']}")
        
        # 3. PREPARAR DECISÃO COMPLETA
        decisao_completa = {
            "score_tendencia": score_tendencia,
            "score_ciclo": score_ciclo,
            "matriz_id": estrategia["id"],
            "fase_operacional": estrategia["fase_operacional"],
            "alavancagem": float(estrategia["alavancagem"]),
            "satelite": float(estrategia["satelite"]),
            "acao": estrategia["acao"],
            "tendencia": estrategia["tendencia"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # 4. GRAVAR HISTÓRICO
        sucesso_gravacao = inserir_decisao(decisao_completa)
        if not sucesso_gravacao:
            logger.warning("⚠️ Falha ao gravar histórico - decisão processada mas não salva")
        
        # 5. RESPOSTA FINAL
        logger.info(f"✅ Decisão Estratégica: {decisao_completa['fase_operacional']} - {decisao_completa['tendencia']}")
        
        return {
            "status": "success",
            "timestamp": decisao_completa["timestamp"],
            "decisao": {
                "fase_operacional": decisao_completa["fase_operacional"],
                "tendencia": decisao_completa["tendencia"],
                "alavancagem": decisao_completa["alavancagem"],
                "satelite_percentual": f"{decisao_completa['satelite']*100:.0f}%",
                "acao_primaria": decisao_completa["acao"]
            },
            "scores": {
                "tendencia": score_tendencia,
                "ciclo": score_ciclo
            },
            "detalhes": {
                "matriz_id": decisao_completa["matriz_id"],
                "satelite_decimal": decisao_completa["satelite"],
                "gravado_historico": sucesso_gravacao
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na Decisão Estratégica: {str(e)}")
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "erro": str(e),
            "decisao": None
        }

def obter_ultima_estrategia() -> Dict:
    """
    Obtém última decisão estratégica do histórico
    
    Returns:
        Dict com última decisão ou erro
    """
    try:
        logger.info("🔍 Obtendo última estratégia...")
        
        ultima_decisao = get_ultima_decisao()
        
        if ultima_decisao:
            return {
                "status": "success",
                "timestamp": ultima_decisao["timestamp"].isoformat(),
                "decisao": {
                    "fase_operacional": ultima_decisao["fase_operacional"],
                    "tendencia": ultima_decisao["tendencia"],
                    "alavancagem": float(ultima_decisao["alavancagem"]),
                    "satelite_percentual": f"{float(ultima_decisao['satelite'])*100:.0f}%",
                    "acao_primaria": ultima_decisao["acao"]
                },
                "scores": {
                    "tendencia": ultima_decisao["score_tendencia"],
                    "ciclo": ultima_decisao["score_ciclo"]
                }
            }
        else:
            return {
                "status": "not_found",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Nenhuma decisão estratégica encontrada no histórico"
            }
            
    except Exception as e:
        logger.error(f"❌ Erro ao obter última estratégia: {str(e)}")
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "erro": str(e)
        }

def debug_matriz_estrategica() -> Dict:
    """
    Debug da matriz estratégica - validação e status
    
    Returns:
        Dict com status da matriz
    """
    try:
        logger.info("🔍 Debug da matriz estratégica...")
        
        validacao = validar_matriz_completa()
        
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "matriz": validacao
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no debug da matriz: {str(e)}")
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "erro": str(e)
        }

def _buscar_scores() -> Optional[Dict]:
    """
    Busca scores de tendência e ciclo
    
    Returns:
        Dict com scores ou None se falhar
    """
    try:
        # 1. SCORE TENDÊNCIA (via helper)
        dados_tendencia = obter_score_tendencia()
        if not dados_tendencia:
            raise Exception("Score tendência não disponível")
        
        score_tendencia = dados_tendencia.get("score_emas")
        if score_tendencia is None:
            raise Exception("Score tendência inválido")
        
        # 2. SCORE CICLO (via service)
        resultado_ciclo = calcular_score_ciclo()
        if resultado_ciclo.get("status") != "success":
            raise Exception("Falha ao calcular score ciclo")
        
        score_ciclo = float(resultado_ciclo["score_consolidado"])
        
        # 3. VALIDAR RANGES
        if not (0 <= score_tendencia <= 100):
            raise Exception(f"Score tendência fora do range: {score_tendencia}")
        
        if not (0 <= score_ciclo <= 100):
            raise Exception(f"Score ciclo fora do range: {score_ciclo}")
        
        return {
            "score_tendencia": int(score_tendencia),
            "score_ciclo": int(score_ciclo)
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar scores: {str(e)}")
        return None