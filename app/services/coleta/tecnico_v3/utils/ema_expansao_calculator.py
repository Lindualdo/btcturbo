# app/services/scores/tecnico_v3/utils/ema_expansao_calculator.py

import logging
from typing import Dict
from .expansao_total_calculator import calcular_expansao_total
from .expansao_critica_calculator import calcular_expansao_critica
from .expansao_adjacente_calculator import calcular_expansao_adjacente

logger = logging.getLogger(__name__)

def calcular_score_expansao(emas: Dict[str, float], timeframe: str = "semanal") -> Dict:
    """
    Calcula Score Expansão v3.1 - Sistema 3 Níveis
    
    Composição:
    - Expansão Total (40%): EMA17/EMA610
    - Expansão Crítica (40%): EMA17/EMA144  
    - Expansão Adjacente (20%): EMAs consecutivas
    
    Score = 100 - (Total×0.4 + Crítica×0.4 + Adjacente×0.2)
    """
    try:
        logger.info(f"📐 Calculando Score Expansão v3.1 - {timeframe}...")
        
        # Validar EMAs
        emas_necessarias = [17, 34, 144, 305, 610]
        for ema in emas_necessarias:
            if ema not in emas or emas[ema] is None:
                raise ValueError(f"EMA {ema} não encontrada")
        
        # Calcular 3 componentes
        total_result = calcular_expansao_total(emas[17], emas[610], timeframe)
        critica_result = calcular_expansao_critica(emas[17], emas[144], timeframe)
        adjacente_result = calcular_expansao_adjacente(emas, timeframe)
        
        # Aplicar pesos e calcular score final
        penalidade_total = (
            total_result["penalidade"] * 0.4 +
            critica_result["penalidade"] * 0.4 +
            adjacente_result["penalidade"] * 0.2
        )
        
        score_final = max(0, 100 - penalidade_total)
        
        logger.info(f"✅ Score Expansão {timeframe}: {score_final:.1f}/100")
        
        return {
            "score": round(score_final, 1),
            "penalidade_total": round(penalidade_total, 1),
            "componentes": {
                "expansao_total": total_result,
                "expansao_critica": critica_result, 
                "expansao_adjacente": adjacente_result
            },
            "interpretacao": _interpretar_expansao(score_final),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro calcular expansão: {str(e)}")
        return {
            "score": 0,
            "penalidade_total": 100,
            "componentes": {},
            "interpretacao": "erro",
            "status": "error",
            "erro": str(e)
        }

def _interpretar_expansao(score: float) -> Dict:
    """Interpreta score de expansão"""
    if score >= 90:
        return {"classificacao": "EMAs Compactadas", "nivel": "excelente"}
    elif score >= 70:
        return {"classificacao": "Expansão Moderada", "nivel": "bom"}
    elif score >= 50:
        return {"classificacao": "Expansão Significativa", "nivel": "alerta"}
    elif score >= 25:
        return {"classificacao": "Alta Dispersão", "nivel": "cuidado"}
    else:
        return {"classificacao": "Dispersão Extrema", "nivel": "critico"}