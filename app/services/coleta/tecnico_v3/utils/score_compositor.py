# app/services/coleta/tecnico_v3/utils/score_compositor.py - CORRIGIDO

import logging
from typing import Dict
from .ema_alinhamento_calculator import calcular_score_alinhamento
from .ema_expansao_calculator import calcular_score_expansao

logger = logging.getLogger(__name__)

def calcular_score_tecnico_v3(emas_semanal: Dict, emas_diario: Dict) -> Dict:
    """Compõe score técnico final v3.0"""
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
                "status": "success",
                "score_consolidado": round(score_final, 1),
                "classificacao_consolidada": _interpretar_score_final(score_final) ,
                "score_consolidado_1w": semanal_scores["score_consolidado"],
                "score_consolidado_1d": diario_scores["score_consolidado"]
                }
    
    except Exception as e:
        logger.error(f"❌ Erro compositor v3.0: {str(e)}")
        return {
            "score_final": 0.0,
            "interpretacao": "erro",
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
        
        score_alinhamento = alinhamento_result["score"]
        score_consolidado = score_alinhamento 
        
        logger.info(f"✅ Score {timeframe}: {score_consolidado:.1f} (Alin:{score_alinhamento}")
        
        return {
            "score_consolidado": round(score_consolidado, 1),
            "alinhamento": {
                "score": score_alinhamento,
                "detalhes": alinhamento_result.get("detalhes", {}),
                "interpretacao": alinhamento_result.get("interpretacao", {})
            },
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro score {timeframe}: {str(e)}")
        return {
            "score_consolidado": 0.0,
            "alinhamento": {},
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