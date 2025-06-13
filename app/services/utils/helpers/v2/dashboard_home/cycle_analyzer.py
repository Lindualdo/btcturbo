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
    Determina ciclo baseado em MVRV Z-Score e Score de Mercado
    
    Tabela de referência (docs):
    - Score 0-20: BOTTOM
    - Score 20-40: ACUMULAÇÃO  
    - Score 40-60: BULL INICIAL
    - Score 60-80: BULL MADURO
    - Score 80-100: EUFORIA/TOPO
    """
    
    # Prioridade: Score de Mercado (mais atual)
    if score <= 20:
        return {
            "cycle": "BOTTOM",
            "phase": "acumulacao_agressiva", 
            "direction": "comprar",
            "max_leverage": 3.0,
            "stop_suggested": 20,
            "position_size": "40-50%"
        }
    elif score <= 40:
        return {
            "cycle": "ACUMULAÇÃO", 
            "phase": "compras_agressivas",
            "direction": "comprar",
            "max_leverage": 2.5,
            "stop_suggested": 15,
            "position_size": "30-40%"
        }
    elif score <= 60:
        return {
            "cycle": "BULL_INICIAL",
            "phase": "compras_moderadas", 
            "direction": "comprar_seletivo",
            "max_leverage": 2.5,
            "stop_suggested": 12,
            "position_size": "20-30%"
        }
    elif score <= 80:
        return {
            "cycle": "BULL_MADURO",
            "phase": "hold_realizacoes",
            "direction": "hold_realizar",
            "max_leverage": 2.0,
            "stop_suggested": 10,
            "position_size": "15-25%"
        }
    else:  # score > 80
        return {
            "cycle": "EUFORIA_TOPO",
            "phase": "realizar_gradual",
            "direction": "realizar", 
            "max_leverage": 1.5,
            "stop_suggested": 8,
            "position_size": "realizar_20-40%"
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