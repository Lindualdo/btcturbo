# app/services/utils/helpers/v2/dashboard_home/cycle_analyzer.py

import logging
from typing import Dict

logger = logging.getLogger(__name__)

def identify_cycle(data: Dict) -> Dict:
    """
    Identifica ciclo baseado apenas em Score Mercado
    """
    try:
        score_mercado = data["score_mercado"]
        mvrv = data.get("mvrv", 0)
        
        cycle_info = _get_cycle_from_score(score_mercado)
        
        logger.info(f"🔄 Ciclo: {cycle_info['cycle']} (Score: {score_mercado:.1f}, MVRV: {mvrv:.2f})")
        
        return cycle_info
        
    except Exception as e:
        logger.error(f"❌ Erro identificação ciclo: {str(e)}")
        return _get_default_cycle()

def _get_cycle_from_score(score: float) -> Dict:
    """
    Determina ciclo baseado APENAS em Score Mercado
    """
    
    # Score define ciclo diretamente
    if score <= 20:
        cycle = "BOTTOM"
    elif score <= 40:
        cycle = "ACUMULAÇÃO"
    elif score <= 60:
        cycle = "BULL_INICIAL"
    elif score <= 80:
        cycle = "BULL_MADURO"
    else:
        cycle = "EUFORIA_TOPO"
    
    # Tabela de parâmetros
    params = {
        "BOTTOM": {
            "max_leverage": 3.0,
            "max_exposure": 100,
            "stop_suggested": -20,
            "position_size": "40-50%",
            "stop_type": "MA"
        },
        "ACUMULAÇÃO": {
            "max_leverage": 2.5,
            "max_exposure": 90,
            "stop_suggested": -15,
            "position_size": "30-40%",
            "stop_type": "MA"
        },
        "BULL_INICIAL": {
            "max_leverage": 2.5,
            "max_exposure": 100,
            "stop_suggested": -12,
            "position_size": "20-30%",
            "stop_type": "MA"
        },
        "BULL_MADURO": {
            "max_leverage": 2.0,
            "max_exposure": 80,
            "stop_suggested": -10,
            "position_size": "15-25%",
            "stop_type": "ATR"
        },
        "EUFORIA_TOPO": {
            "max_leverage": 1.5,
            "max_exposure": 60,
            "stop_suggested": -8,
            "position_size": "Realize 20-40%",
            "stop_type": "ATR"
        }
    }
    
    p = params[cycle]
    
    return {
        "cycle": cycle,
        "phase": f"{cycle.lower()}_phase",
        "direction": "comprar" if score <= 60 else "realizar",
        "max_leverage": p["max_leverage"],
        "max_exposure": p["max_exposure"],
        "stop_suggested": p["stop_suggested"],
        "position_size": p["position_size"],
        "stop_type": p["stop_type"],
        "interpretation": f"Score {score:.1f} → {cycle}"
    }

def _get_default_cycle() -> Dict:
    """Ciclo padrão em caso de erro"""
    return {
        "cycle": "NEUTRO",
        "phase": "indefinido",
        "direction": "hold",
        "max_leverage": 2.0,
        "max_exposure": 70,
        "stop_suggested": -12,
        "position_size": "0%",
        "stop_type": "MA",
        "interpretation": "Dados insuficientes"
    }

def get_cycle_permissions(cycle_info: Dict) -> Dict:
    """Retorna permissões baseadas no ciclo"""
    cycle = cycle_info["cycle"]
    
    permissions = {
        "BOTTOM": {"allow_buy": True, "allow_sell": False, "priority": "maxima"},
        "ACUMULAÇÃO": {"allow_buy": True, "allow_sell": False, "priority": "alta"},
        "BULL_INICIAL": {"allow_buy": True, "allow_sell": False, "priority": "media"},
        "BULL_MADURO": {"allow_buy": True, "allow_sell": True, "priority": "baixa_compra"},
        "EUFORIA_TOPO": {"allow_buy": False, "allow_sell": True, "priority": "maxima_venda"}
    }
    
    return permissions.get(cycle, {"allow_buy": True, "allow_sell": True, "priority": "media"})