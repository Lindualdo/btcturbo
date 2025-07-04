# services/coleta/tendencia/utils/ema_score_calculator.py

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

def calculate_ema_score(current_price, emas):
    """
    Calcula o Bull Score baseado na posição das EMAs
    Retorna score e detalhes das condições avaliadas
    """
    BULL_SCORE = 0
    detalhes = {}

    # Preço vs EMA10: +/-10 pontos
    if current_price > emas[10]: 
        BULL_SCORE += 10
        detalhes["Price_vs_EMA10"] = {"status": "bullish", "pontos": 10}
    elif current_price < emas[10]: 
        BULL_SCORE -= 10
        detalhes["Price_vs_EMA10"] = {"status": "bearish", "pontos": -10}
    else:
        detalhes["Price_vs_EMA10"] = {"status": "neutral", "pontos": 0}

    # EMA10 vs EMA20: +/-15 pontos
    if emas[10] > emas[20]: 
        BULL_SCORE += 15
        detalhes["10_vs_20"] = {"status": "bullish", "pontos": 15}
    elif emas[10] < emas[20]: 
        BULL_SCORE -= 15
        detalhes["10_vs_20"] = {"status": "bearish", "pontos": -15}
    else:
        detalhes["10_vs_20"] = {"status": "neutral", "pontos": 0}

    # EMA20 vs EMA50: +/-20 pontos
    if emas[20] > emas[50]: 
        BULL_SCORE += 20
        detalhes["20_vs_50"] = {"status": "bullish", "pontos": 20}
    elif emas[20] < emas[50]: 
        BULL_SCORE -= 20
        detalhes["20_vs_50"] = {"status": "bearish", "pontos": -20}
    else:
        detalhes["20_vs_50"] = {"status": "neutral", "pontos": 0}

    # EMA50 vs EMA100: +/-25 pontos
    if emas[50] > emas[100]: 
        BULL_SCORE += 25
        detalhes["50_vs_100"] = {"status": "bullish", "pontos": 25}
    elif emas[50] < emas[100]: 
        BULL_SCORE -= 25
        detalhes["50_vs_100"] = {"status": "bearish", "pontos": -25}
    else:
        detalhes["50_vs_100"] = {"status": "neutral", "pontos": 0}

    # EMA100 vs EMA200: +/-30 pontos
    if emas[100] > emas[200]: 
        BULL_SCORE += 30
        detalhes["100_vs_200"] = {"status": "bullish", "pontos": 30}
    elif emas[100] < emas[200]: 
        BULL_SCORE -= 30
        detalhes["100_vs_200"] = {"status": "bearish", "pontos": -30}
    else:
        detalhes["100_vs_200"] = {"status": "neutral", "pontos": 0}
    

    # Normalização para escala 0-100
    score_normalizado = max(0, min(100, (BULL_SCORE + 100) // 2))

    ema_score = {
        "score": score_normalizado,
        "classificacao": _interpretar_alinhamento(score_normalizado),
        "detalhes": detalhes
    }

    return ema_score

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