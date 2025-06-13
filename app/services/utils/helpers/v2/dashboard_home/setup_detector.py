# app/services/utils/helpers/v2/dashboard_home/setup_detector.py

import logging
from typing import Dict

logger = logging.getLogger(__name__)

def detect_setup_4h(data: Dict) -> Dict:
    """
    Detecta setup baseado em EMA144 distance e RSI (timeframe 4H logic)
    
    Returns:
        Dict com setup detectado e confiança
    """
    try:
        ema_distance = data["ema_distance"]
        rsi_diario = data["rsi_diario"]
        
        # Detectar setup principal
        setup_info = _identify_primary_setup(ema_distance, rsi_diario)
        
        logger.info(f"🎯 Setup detectado: {setup_info['setup']} (EMA: {ema_distance:+.1f}%, RSI: {rsi_diario:.1f})")
        
        return setup_info
        
    except Exception as e:
        logger.error(f"❌ Erro detecção setup: {str(e)}")
        return {
            "setup": "NEUTRO",
            "confidence": "baixa",
            "action": "HOLD",
            "size": 0
        }

def _identify_primary_setup(ema_distance: float, rsi: float) -> Dict:
    """
    Identifica setup principal baseado na matriz de decisão
    """
    
    # SETUPS DE COMPRA (quando permitido pelo ciclo)
    if _is_pullback_setup(ema_distance, rsi):
        return {
            "setup": "PULLBACK_TENDENCIA",
            "confidence": "alta",
            "action": "COMPRAR", 
            "size": 30,
            "description": "Pullback em tendência de alta"
        }
    
    if _is_support_test_setup(ema_distance, rsi):
        return {
            "setup": "TESTE_SUPORTE",
            "confidence": "media",
            "action": "COMPRAR",
            "size": 25,
            "description": "Teste do suporte EMA144"
        }
        
    if _is_breakout_setup(ema_distance, rsi):
        return {
            "setup": "ROMPIMENTO",
            "confidence": "alta",
            "action": "COMPRAR",
            "size": 20,
            "description": "Rompimento de resistência"
        }
        
    if _is_oversold_extreme_setup(ema_distance, rsi):
        return {
            "setup": "OVERSOLD_EXTREMO", 
            "confidence": "maxima",
            "action": "COMPRAR",
            "size": 40,
            "description": "Oversold extremo com divergência"
        }
    
    # SETUPS DE VENDA
    if _is_resistance_setup(ema_distance, rsi):
        return {
            "setup": "RESISTENCIA",
            "confidence": "alta", 
            "action": "REALIZAR",
            "size": 25,
            "description": "Resistência com RSI alto"
        }
        
    if _is_exhaustion_setup(ema_distance, rsi):
        return {
            "setup": "EXAUSTAO",
            "confidence": "media",
            "action": "REALIZAR", 
            "size": 30,
            "description": "Sinais de exaustão"
        }
    
    # NEUTRO
    return {
        "setup": "NEUTRO",
        "confidence": "baixa",
        "action": "HOLD",
        "size": 0,
        "description": "Nenhum setup claro detectado"
    }

def _is_pullback_setup(ema_distance: float, rsi: float) -> bool:
    """RSI < 45 + EMA144 ±3%"""
    return rsi < 45 and -3 <= ema_distance <= 3

def _is_support_test_setup(ema_distance: float, rsi: float) -> bool:
    """Toca EMA144 (distance próximo de 0)"""
    return -2 <= ema_distance <= 2 and 30 <= rsi <= 60

def _is_breakout_setup(ema_distance: float, rsi: float) -> bool:
    """Fecha acima resistência (ema_distance > 5% com RSI moderado)"""
    return ema_distance > 5 and 45 <= rsi <= 65

def _is_oversold_extreme_setup(ema_distance: float, rsi: float) -> bool:
    """RSI < 30 (oversold extremo)"""
    return rsi < 30

def _is_resistance_setup(ema_distance: float, rsi: float) -> bool:
    """RSI > 70 + distância alta da EMA"""
    return rsi > 70 and ema_distance > 10

def _is_exhaustion_setup(ema_distance: float, rsi: float) -> bool:
    """RSI alto + distância moderada (possível topo)"""
    return rsi > 65 and 5 <= ema_distance <= 15

def get_setup_confluence(setup_info: Dict, data: Dict) -> Dict:
    """
    Avalia confluência do setup com outros indicadores
    """
    confluences = []
    
    # Confluência com MVRV
    mvrv = data["mvrv"]
    if setup_info["action"] == "COMPRAR" and mvrv < 1.5:
        confluences.append("MVRV_FAVORAVEL")
    elif setup_info["action"] == "REALIZAR" and mvrv > 2.5:
        confluences.append("MVRV_ALERTA")
    
    # Confluência com Health Factor
    hf = data["health_factor"]
    if hf > 1.5:
        confluences.append("RISCO_BAIXO")
    elif hf < 1.3:
        confluences.append("RISCO_ALTO")
    
    return {
        "confluences": confluences,
        "strength": len(confluences),
        "validated": len(confluences) >= 1
    }