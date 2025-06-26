# source: app/services/dashboards/dash_mercado/score_calculator.py

import logging
 # Importar funções de score existentes
from app.services.scores import ciclos as score_ciclos
from app.services.scores import momentum as score_momentum
from app.services.scores.tecnico  import calcular_score as calcular_score_tecnico

logger = logging.getLogger(__name__)

def calculate_all_scores() -> dict:
    """
    Calcula scores de todos os blocos usando funções existentes
    
    Args:
        dados_coletados: {"ciclo": {}, "momentum": {}, "tecnico": {}}
        
    Returns:
        dict: {"status": "success/error", "scores": {todos_os_scores}}
    """
    try:
        logger.info("🧮 Calculando scores dos 3 blocos...")

        # Calcular scores individuais
        resultado_ciclo = _calculate_ciclo_score(score_ciclos)
        resultado_momentum = _calculate_momentum_score(score_momentum) 
        resultado_tecnico = calcular_score_tecnico()
        
        # Verificar se todos os scores foram calculados
        if not resultado_ciclo or not resultado_momentum or not resultado_tecnico:
            return {
                "status": "error",
                "erro": "Falha no cálculo de um ou mais scores"
            }
        
        # Consolidar todos os scores
        scores_consolidados = {
            "score_ciclo": resultado_ciclo["score"] ,
            "classificacao_ciclo": resultado_ciclo["classificacao"],
            "score_momentum": resultado_momentum["score"],
            "classificacao_momentum": resultado_momentum["classificacao"],
            "score_tecnico": resultado_tecnico["score_consolidado"], 
            "classificacao_tecnico": resultado_tecnico["classificacao_consolidada"]
        }
        
        logger.info("✅ Todos os scores calculados")
        return {
            "status": "success",
            "scores": scores_consolidados
        }
        
    except Exception as e:
        logger.error(f"❌ Erro calculate_all_scores: {str(e)}")
        return {
            "status": "error",
            "erro": str(e)
        }

def _calculate_ciclo_score(score_ciclos) -> dict:
    """Calcula score do bloco CICLO"""
    try:
        resultado = score_ciclos.calcular_score()
        
        if resultado.get("status") == "success":
            # Ciclos retorna "score_consolidado" e "classificacao_consolidada"
            score = resultado.get("score_consolidado", resultado.get("score", 0))
            classificacao = resultado.get("classificacao_consolidada", resultado.get("classificacao", "neutro"))
            
            logger.info(f"✅ Score CICLO: {score:.1f}")
            return {
                "score": score * 10,
                "classificacao": classificacao
            }
        else:
            logger.error("❌ Falha cálculo score CICLO")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro _calculate_ciclo_score: {str(e)}")
        return None

def _calculate_momentum_score(score_momentum) -> dict:
    """Calcula score do bloco MOMENTUM"""
    try:
        resultado = score_momentum.calcular_score()
        
        if resultado.get("status") == "success":
            # Momentum retorna "score_consolidado" e "classificacao_consolidada"
            score = resultado.get("score_consolidado", resultado.get("score", 0))
            classificacao = resultado.get("classificacao_consolidada", resultado.get("classificacao", "neutro"))
            
            logger.info(f"✅ Score MOMENTUM: {score:.1f}")
            return {
                "score": score * 10,
                "classificacao": classificacao
            }
        else:
            logger.error("❌ Falha cálculo score MOMENTUM")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro _calculate_momentum_score: {str(e)}")
        return None

    """Calcula score do bloco TÉCNICO"""
    try:
        resultado = calcular_score_tecnico()
        
        if resultado.get("status") == "success":
            # Técnico pode retornar "score" ou "score_consolidado"
            score = resultado.get("score_consolidado", resultado.get("score", 0))
            classificacao = resultado.get("classificacao_consolidada", resultado.get("classificacao", "neutro"))
            
            logger.info(f"✅ Score TÉCNICO: {score:.1f}")
            return {
                "score": score,
                "classificacao": classificacao
            }
        else:
            logger.error("❌ Falha cálculo score TÉCNICO")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro _calculate_tecnico_score: {str(e)}")
        return None