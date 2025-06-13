# app/services/utils/helpers/v2/dashboard_home/cycle_analyzer.py

import logging
from typing import Dict

logger = logging.getLogger(__name__)

def identify_cycle(data: Dict) -> Dict:
    """
    Identifica ciclo de mercado baseado em MVRV e Score
    
    Returns:
        Dict com ciclo, fase, direção permitida
    """
    try:
        mvrv = data["mvrv"]
        score_mercado = data["score_mercado"]
        
        # Tabela de ciclos (baseada na documentação)
        cycle_info = _get_cycle_from_mvrv_score(mvrv, score_mercado)
        
        logger.info(f"🔄 Ciclo identificado: {cycle_info['cycle']} (MVRV: {mvrv:.2f}, Score: {score_mercado:.1f})")
        
        return cycle_info
        
    except Exception as e:
        logger.error(f"❌ Erro identificação ciclo: {str(e)}")
        return {
            "cycle": "NEUTRO",
            "phase": "indefinido",
            "direction": "hold",
            "max_leverage": 2.0,
            "stop_suggested": 12
        }

def _get_cycle_from_mvrv_score(mvrv: float, score: float) -> Dict:
    """
    Determina ciclo baseado em COMBINAÇÃO Score + MVRV (conforme documentação)
    
    Tabela oficial:
    - Score 0-20 + MVRV <0.8: BOTTOM
    - Score 20-40 + MVRV 0.8-1.2: ACUMULAÇÃO  
    - Score 40-60 + MVRV 1.2-2.0: BULL INICIAL
    - Score 60-80 + MVRV 2.0-3.0: BULL MADURO
    - Score 80-100 + MVRV >3.0: EUFORIA/TOPO
    """
    
    # Combinação Score + MVRV (ambos devem confluir)
    if score <= 20 and mvrv < 0.8:
        return {
            "cycle": "BOTTOM",
            "phase": "acumulacao_agressiva", 
            "direction": "comprar",
            "max_leverage": 3.0,
            "stop_suggested": 20,
            "position_size": "40-50%"
        }
    elif score <= 40 and 0.8 <= mvrv <= 1.2:
        return {
            "cycle": "ACUMULAÇÃO", 
            "phase": "compras_agressivas",
            "direction": "comprar",
            "max_leverage": 2.5,
            "stop_suggested": 15,
            "position_size": "30-40%"
        }
    elif score <= 60 and 1.2 <= mvrv <= 2.0:
        return {
            "cycle": "BULL_INICIAL",
            "phase": "compras_moderadas", 
            "direction": "comprar_seletivo",
            "max_leverage": 2.5,
            "stop_suggested": 12,
            "position_size": "20-30%"
        }
    elif score <= 80 and 2.0 <= mvrv <= 3.0:
        return {
            "cycle": "BULL_MADURO",
            "phase": "hold_realizacoes",
            "direction": "hold_realizar",
            "max_leverage": 2.0,
            "stop_suggested": 10,
            "position_size": "15-25%"
        }
    elif score > 80 and mvrv > 3.0:
        return {
            "cycle": "EUFORIA_TOPO",
            "phase": "realizar_gradual",
            "direction": "realizar", 
            "max_leverage": 1.5,
            "stop_suggested": 8,
            "position_size": "realizar_20-40%"
        }
    else:
        # Conflito Score vs MVRV - critério de desempate
        if mvrv >= 3.0:
            priority_cycle = "EUFORIA_TOPO"
            max_lev = 1.5
        elif mvrv >= 2.0:
            priority_cycle = "BULL_MADURO" 
            max_lev = 2.0
        elif mvrv >= 1.2:
            priority_cycle = "BULL_INICIAL"
            max_lev = 2.5
        elif mvrv >= 0.8:
            priority_cycle = "ACUMULAÇÃO"
            max_lev = 2.5
        else:
            priority_cycle = "BOTTOM"
            max_lev = 3.0
            
        return {
            "cycle": f"{priority_cycle}_CONFLITO",
            "phase": "conflito_indicadores",
            "direction": "cautela",
            "max_leverage": max_lev,
            "stop_suggested": 12,
            "position_size": "reduzido",
            "alert": f"Conflito: Score={score:.1f}, MVRV={mvrv:.2f}"
        }

def get_cycle_permissions(cycle_info: Dict) -> Dict:
    """
    Retorna permissões baseadas no ciclo identificado
    """
    cycle = cycle_info["cycle"]
    
    permissions = {
        "BOTTOM": {
            "allow_buy": True,
            "allow_sell": False,
            "priority": "maxima",
            "bias": "acumular"
        },
        "ACUMULAÇÃO": {
            "allow_buy": True, 
            "allow_sell": False,
            "priority": "alta",
            "bias": "comprar"
        },
        "BULL_INICIAL": {
            "allow_buy": True,
            "allow_sell": False, 
            "priority": "media",
            "bias": "seletivo"
        },
        "BULL_MADURO": {
            "allow_buy": True,
            "allow_sell": True,
            "priority": "baixa_compra",
            "bias": "realizar_parcial"
        },
        "EUFORIA_TOPO": {
            "allow_buy": False,
            "allow_sell": True,
            "priority": "maxima_venda", 
            "bias": "realizar"
        }
    }
    
    return permissions.get(cycle, {
        "allow_buy": True,
        "allow_sell": True, 
        "priority": "media",
        "bias": "neutro"
    })