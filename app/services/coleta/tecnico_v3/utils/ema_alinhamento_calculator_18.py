# app/services/scores/tecnico_v3/utils/ema_alinhamento_calculator.py

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

def calcular_score_alinhamento(emas: Dict[str, float]) -> Dict:
    """
    Calcula Score Alinhamento baseado na v1.8
    
    Regras:
    - Preço > EMA 10: 10 pontos
    - EMA 10 > EMA 20: 15 pontos
    - EMA 20 > EMA 50: 20 pontos  
    - EMA 50 > EMA 100: 25 pontos
    - EMA 100 > EMA 200: 30 pontos
    Total máximo: 100 pontos
    
    Args:
        emas: Dict com valores das EMAs {10: valor, 34: valor, ...}
        
    Returns:
        {
            "score": int (0-100),
            "detalhes": dict,
            "status": str
        }
    """
    try:
        logger.info("📊 Calculando Score Alinhamento v1.8...")
        
        # Validar EMAs obrigatórias
        emas_necessarias = [10, 20, 50, 100, 200]
        for ema in emas_necessarias:
            if ema not in emas or emas[ema] is None:
                raise ValueError(f"EMA {ema} não encontrada ou nula")
        
        score = 0
        detalhes = {}
        
        # EMA Preço acima da EMA10: 10 pontos
        if emas["current_price"] > emas[10]:
            score += 10
            detalhes["Price>EMA_10"] = {"status": "bullish", "pontos": 10}
        else:
            detalhes["10_vs_20"] = {"status": "bearish", "pontos": 0}


        # EMA 10 > EMA 20: 15 pontos
        if emas[10] > emas[20]:
            score += 10
            detalhes["10_vs_20"] = {"status": "bullish", "pontos": 15}
        else:
            detalhes["10_vs_20"] = {"status": "bearish", "pontos": 0}
            
        # EMA 20 > EMA 50: 20 pontos
        if emas[20] > emas[50]:
            score += 20
            detalhes["20_vs_50"] = {"status": "bullish", "pontos": 20}
        else:
            detalhes["20_vs_50"]  = {"status": "bearish", "pontos": 0}
            
        # EMA 50 > EMA 100: 25 pontos
        if emas[50] > emas[100]:
            score += 25
            detalhes["50_vs_100"] = {"status": "bullish", "pontos": 25}
        else:
            detalhes["50_vs_100"] = {"status": "bearish", "pontos": 0}
            
        # EMA 100 > EMA 200: 30 pontos
        if emas[100] > emas[200]:
            score += 40
            detalhes["100_vs_200"] = {"status": "bullish", "pontos": 30}
        else:
            detalhes["100_vs_200"] = {"status": "bearish", "pontos": 0}
        
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