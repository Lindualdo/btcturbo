# app/services/scores/tecnico_v3/utils/ema_alinhamento_calculator.py

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

def calcular_score_alinhamento(emas: Dict[str, float]) -> Dict:
    """
    Calcula Score Alinhamento baseado na v3.0
    
    Regras:
    - EMA 17 > EMA 34: 10 pontos
    - EMA 34 > EMA 144: 20 pontos  
    - EMA 144 > EMA 305: 30 pontos
    - EMA 305 > EMA 610: 40 pontos
    Total máximo: 100 pontos
    
    Args:
        emas: Dict com valores das EMAs {17: valor, 34: valor, ...}
        
    Returns:
        {
            "score": int (0-100),
            "detalhes": dict,
            "status": str
        }
    """
    try:
        logger.info("📊 Calculando Score Alinhamento v3.0...")
        
        # Validar EMAs obrigatórias
        emas_necessarias = [17, 34, 144, 305, 610]
        for ema in emas_necessarias:
            if ema not in emas or emas[ema] is None:
                raise ValueError(f"EMA {ema} não encontrada ou nula")
        
        score = 0
        detalhes = {}
        
        # EMA 17 > EMA 34: 10 pontos
        if emas[17] > emas[34]:
            score += 10
            detalhes["17_vs_34"] = {"status": "bullish", "pontos": 10}
        else:
            detalhes["17_vs_34"] = {"status": "bearish", "pontos": 0}
            
        # EMA 34 > EMA 144: 20 pontos
        if emas[34] > emas[144]:
            score += 20
            detalhes["34_vs_144"] = {"status": "bullish", "pontos": 20}
        else:
            detalhes["34_vs_144"] = {"status": "bearish", "pontos": 0}
            
        # EMA 144 > EMA 305: 30 pontos
        if emas[144] > emas[305]:
            score += 30
            detalhes["144_vs_305"] = {"status": "bullish", "pontos": 30}
        else:
            detalhes["144_vs_305"] = {"status": "bearish", "pontos": 0}
            
        # EMA 305 > EMA 610: 40 pontos
        if emas[305] > emas[610]:
            score += 40
            detalhes["305_vs_610"] = {"status": "bullish", "pontos": 40}
        else:
            detalhes["305_vs_610"] = {"status": "bearish", "pontos": 0}
        
        logger.info(f"✅ Score Alinhamento calculado: {score}/100")
        
        return {
            "score": score,
            "detalhes": detalhes,
            "interpretacao": _interpretar_alinhamento(score),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro calcular alinhamento: {str(e)}")
        return {
            "score": 0,
            "detalhes": {},
            "interpretacao": "erro",
            "status": "error",
            "erro": str(e)
        }

def _interpretar_alinhamento(score: int) -> Dict:
    """Interpreta score de alinhamento"""
    if score == 100:
        return {
            "classificacao": "Alinhamento Bullish Perfeito",
            "descricao": "Todas as EMAs em formação bullish",
            "nivel": "forte"
        }
    elif score >= 70:
        return {
            "classificacao": "Estrutura Bullish Dominante", 
            "descricao": "Maioria das EMAs alinhadas bullish",
            "nivel": "bom"
        }
    elif score >= 40:
        return {
            "classificacao": "Mercado em Transição",
            "descricao": "EMAs parcialmente alinhadas",
            "nivel": "neutro"
        }
    elif score >= 10:
        return {
            "classificacao": "Estrutura Bearish Formando",
            "descricao": "Poucas EMAs em alinhamento bullish",
            "nivel": "fraco"
        }
    else:
        return {
            "classificacao": "Bear Market Confirmado",
            "descricao": "Nenhuma EMA em alinhamento bullish",
            "nivel": "critico"
        }