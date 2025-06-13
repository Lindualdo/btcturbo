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
    Determina ciclo baseado em MVRV (prioritário) com validação de Score
    
    Tabela atualizada - MVRV define ciclo, Score valida:
    - MVRV < 0.8: BOTTOM (Score esperado 0-20)
    - MVRV 0.8-1.2: ACUMULAÇÃO (Score esperado 20-40)
    - MVRV 1.2-2.0: BULL INICIAL (Score esperado 40-70)
    - MVRV 2.0-3.0: BULL MADURO (Score esperado 50-80)
    - MVRV > 3.0: EUFORIA/TOPO (Score esperado 60-100)
    """
    
    # MVRV define o ciclo (prioritário)
    if mvrv < 0.8:
        cycle = "BOTTOM"
        expected_score = (0, 20)
        interpretation = "Oportunidade histórica" if score > 20 else "Bottom confirmado"
        return {
            "cycle": "BOTTOM",
            "phase": "acumulacao_agressiva",
            "direction": "comprar",
            "max_leverage": 3.0,
            "stop_suggested": 20,
            "position_size": "40-50%",
            "interpretation": interpretation
        }
    
    elif 0.8 <= mvrv <= 1.2:
        cycle = "ACUMULAÇÃO"
        expected_score = (20, 40)
        interpretation = "Aumentar posições" if score > 40 else "Acumulação confirmada"
        return {
            "cycle": "ACUMULAÇÃO",
            "phase": "compras_agressivas",
            "direction": "comprar",
            "max_leverage": 2.5,
            "stop_suggested": 15,
            "position_size": "30-40%",
            "interpretation": interpretation
        }
    
    elif 1.2 <= mvrv <= 2.0:
        cycle = "BULL_INICIAL"
        expected_score = (40, 70)
        interpretation = "Comprar pullbacks" if score < 40 else "Bull inicial confirmado"
        return {
            "cycle": "BULL_INICIAL",
            "phase": "compras_moderadas",
            "direction": "comprar_seletivo",
            "max_leverage": 2.5,
            "stop_suggested": 12,
            "position_size": "20-30%",
            "interpretation": interpretation
        }
    
    elif 2.0 <= mvrv <= 3.0:
        cycle = "BULL_MADURO"
        expected_score = (50, 80)
        interpretation = "Manter com stops" if score < 50 else "Bull maduro confirmado"
        return {
            "cycle": "BULL_MADURO",
            "phase": "hold_realizacoes",
            "direction": "hold_realizar",
            "max_leverage": 2.0,
            "stop_suggested": 10,
            "position_size": "15-25%",
            "interpretation": interpretation
        }
    
    else:  # mvrv > 3.0
        cycle = "EUFORIA_TOPO"
        expected_score = (60, 100)
        interpretation = "Realizar gradualmente" if score < 60 else "Euforia confirmada"
        return {
            "cycle": "EUFORIA_TOPO",
            "phase": "realizar_gradual",
            "direction": "realizar",
            "max_leverage": 1.5,
            "stop_suggested": 8,
            "position_size": "realizar_20-40%",
            "interpretation": interpretation
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