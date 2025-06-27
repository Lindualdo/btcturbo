# app/services/scores/tecnico_v3/utils/score_compositor_v3.py

import logging
from typing import Dict
from .ema_alinhamento_calculator import calcular_score_alinhamento
from .ema_expansao_calculator import calcular_score_expansao

logger = logging.getLogger(__name__)

def calcular_score_tecnico_v3(emas_semanal: Dict, emas_diario: Dict) -> Dict:
    """
    Compõe score técnico final v3.0
    
    Fórmula:
    Score_TF = (Score Alinhamento × 0.5) + (Score Expansão × 0.5)
    Score_Final = (Score_1W × 0.7) + (Score_1D × 0.3)
    
    Args:
        emas_semanal: EMAs do timeframe semanal
        emas_diario: EMAs do timeframe diário
        
    Returns:
        {
            "score_final": float,
            "timeframes": dict,
            "componentes": dict,
            "status": str
        }
    """
    try:
        logger.info("🔄 Compondo Score Técnico v3.0...")
        
        # Calcular scores semanal
        semanal_scores = _calcular_score_timeframe(emas_semanal, "1W")
        if semanal_scores["status"] != "success":
            raise Exception(f"Erro score semanal: {semanal_scores.get('erro')}")
        
        # Calcular scores diário  
        diario_scores = _calcular_score_timeframe(emas_diario, "1D")
        if diario_scores["status"] != "success":
            raise Exception(f"Erro score diário: {diario_scores.get('erro')}")
        
        # Aplicar pesos: 70% Semanal + 30% Diário
        peso_semanal = 0.7
        peso_diario = 0.3
        
        score_final = (
            semanal_scores["score_consolidado"] * peso_semanal +
            diario_scores["score_consolidado"] * peso_diario
        )
        
        logger.info(f"✅ Score Final v3.0: {score_final:.1f}/100")
        
        return {
            "score_final": round(score_final, 1),
            "timeframes": {
                "semanal": {
                    "peso": peso_semanal,
                    "score_consolidado": semanal_scores["score_consolidado"],
                    "alinhamento": semanal_scores["alinhamento"],
                    "expansao": semanal_scores["expansao"],
                    "detalhes": semanal_scores["detalhes"]
                },
                "diario": {
                    "peso": peso_diario,
                    "score_consolidado": diario_scores["score_consolidado"], 
                    "alinhamento": diario_scores["alinhamento"],
                    "expansao": diario_scores["expansao"],
                    "detalhes": diario_scores["detalhes"]
                }
            },
            "componentes": {
                "alinhamento_peso": 0.5,
                "expansao_peso": 0.5,
                "timeframe_semanal_peso": peso_semanal,
                "timeframe_diario_peso": peso_diario
            },
            "interpretacao": _interpretar_score_final(score_final),
            "versao": "v3.0",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro compositor v3.0: {str(e)}")
        return {
            "score_final": 0.0,
            "timeframes": {},
            "componentes": {},
            "interpretacao": "erro",
            "versao": "v3.0",
            "status": "error",
            "erro": str(e)
        }

def _calcular_score_timeframe(emas: Dict, timeframe: str) -> Dict:
    """Calcula score para um timeframe específico"""
    try:
        logger.info(f"📊 Calculando score {timeframe}...")
        
        # Score Alinhamento
        alinhamento_result = calcular_score_alinhamento(emas)
        if alinhamento_result["status"] != "success":
            raise Exception(f"Erro alinhamento {timeframe}")
        
        # Mapear timeframe para expansão
        timeframe_map = {"1W": "semanal", "1D": "diario"}
        tf_mapped = timeframe_map.get(timeframe, "semanal")
        
        # Score Expansão  
        expansao_result = calcular_score_expansao(emas, tf_mapped)
        if expansao_result["status"] != "success":
            raise Exception(f"Erro expansão {timeframe}")
        
        # Compor score consolidado: 50% Alinhamento + 50% Expansão
        score_alinhamento = alinhamento_result["score"]
        score_expansao = expansao_result["score"]
        
        score_consolidado = (score_alinhamento * 0.5) + (score_expansao * 0.5)
        
        logger.info(f"✅ Score {timeframe}: {score_consolidado:.1f} (Alin:{score_alinhamento} + Exp:{score_expansao})")
        
        return {
            "score_consolidado": round(score_consolidado, 1),
            "alinhamento": {
                "score": score_alinhamento,
                "detalhes": alinhamento_result["detalhes"],
                "interpretacao": alinhamento_result["interpretacao"]
            },
            "expansao": {
                "score": score_expansao,
                "penalidades": expansao_result["penalidades"],
                "distancias": expansao_result["distancias"],
                "interpretacao": expansao_result["interpretacao"]
            },
            "detalhes": {
                "timeframe": timeframe,
                "composicao": "50% Alinhamento + 50% Expansão",
                "emas_utilizadas": list(emas.keys())
            },
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro score {timeframe}: {str(e)}")
        return {
            "score_consolidado": 0.0,
            "alinhamento": {},
            "expansao": {},
            "detalhes": {},
            "status": "error",
            "erro": str(e)
        }

def _interpretar_score_final(score: float) -> Dict:
    """Interpreta score final conforme documentação v3.0"""
    if score >= 80:
        return {
            "classificacao": "Forte",
            "acao": "Posição completa",
            "nivel": "excelente",
            "descricao": "Estrutura técnica sólida"
        }
    elif score >= 60:
        return {
            "classificacao": "Neutro", 
            "acao": "Manter posição",
            "nivel": "bom",
            "descricao": "Condições técnicas favoráveis"
        }
    elif score >= 40:
        return {
            "classificacao": "Alerta",
            "acao": "Reduzir exposição", 
            "nivel": "cuidado",
            "descricao": "Sinais de enfraquecimento técnico"
        }
    else:
        return {
            "classificacao": "Perigo",
            "acao": "Proteção máxima",
            "nivel": "critico", 
            "descricao": "Estrutura técnica comprometida"
        }