# app/services/utils/helpers/v2/dashboard_home/cycle_analyzer.py

import logging
from typing import Dict

logger = logging.getLogger(__name__)

def identify_cycle(data: Dict) -> Dict:
    """
    Identifica ciclo de mercado baseado em Score Mercado + MVRV
    Usa tabela completa de parâmetros por ciclo
    """
    try:
        mvrv = data["mvrv"]
        score_mercado = data["score_mercado"]
        
        # Identificar ciclo usando ambos Score e MVRV
        cycle_info = _get_cycle_from_score_mvrv(score_mercado, mvrv)
        
        logger.info(f"🔄 Ciclo: {cycle_info['cycle']} (Score: {score_mercado:.1f}, MVRV: {mvrv:.2f})")
        
        return cycle_info
        
    except Exception as e:
        logger.error(f"❌ Erro identificação ciclo: {str(e)}")
        return _get_default_cycle()

def _get_cycle_from_score_mvrv(score: float, mvrv: float) -> Dict:
    """
    Determina ciclo baseado em Score Mercado (prioritário) + MVRV (validação)
    Implementa tabela completa de parâmetros
    """
    
    # BOTTOM: Score 0-20 ou MVRV < 0.8
    if score <= 20 or mvrv < 0.8:
        return {
            "cycle": "BOTTOM",
            "phase": "acumulacao_agressiva",
            "direction": "comprar",
            "max_leverage": 3.0,
            "max_exposure": 100,  # % do capital
            "stop_suggested": -20, # % de perda
            "position_size": "40-50%",
            "interpretation": "Oportunidade histórica - máxima agressividade",
            "stop_type": "MA"  # Moving Average based
        }
    
    # ACUMULAÇÃO: Score 20-40 ou MVRV 0.8-1.2
    elif 20 < score <= 40 or (0.8 <= mvrv <= 1.2):
        return {
            "cycle": "ACUMULAÇÃO", 
            "phase": "compras_agressivas",
            "direction": "comprar",
            "max_leverage": 2.5,
            "max_exposure": 90,
            "stop_suggested": -15,
            "position_size": "30-40%",
            "interpretation": "Acumulação ativa - compras agressivas",
            "stop_type": "MA"
        }
    
    # BULL INICIAL: Score 40-60 ou MVRV 1.2-2.0
    elif 40 < score <= 60 or (1.2 <= mvrv <= 2.0):
        return {
            "cycle": "BULL_INICIAL",
            "phase": "compras_moderadas", 
            "direction": "comprar_seletivo",
            "max_leverage": 2.5,
            "max_exposure": 100,
            "stop_suggested": -12,
            "position_size": "20-30%",
            "interpretation": "Bull inicial - compras seletivas",
            "stop_type": "MA"
        }
    
    # BULL MADURO: Score 60-80 ou MVRV 2.0-3.0
    elif 60 < score <= 80 or (2.0 <= mvrv <= 3.0):
        return {
            "cycle": "BULL_MADURO",
            "phase": "hold_realizacoes",
            "direction": "hold_realizar",
            "max_leverage": 2.0,
            "max_exposure": 80,
            "stop_suggested": -10,
            "position_size": "15-25%", 
            "interpretation": "Bull maduro - manter com stops",
            "stop_type": "ATR"  # Average True Range based
        }
    
    # EUFORIA/TOPO: Score > 80 ou MVRV > 3.0
    else:
        return {
            "cycle": "EUFORIA_TOPO",
            "phase": "realizar_gradual",
            "direction": "realizar",
            "max_leverage": 1.5,
            "max_exposure": 60,
            "stop_suggested": -8,
            "position_size": "Realize 20-40%",
            "interpretation": "Euforia/Topo - realizar gradualmente",
            "stop_type": "ATR"
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
        "interpretation": "Dados insuficientes",
        "stop_type": "MA"
    }

def get_cycle_parameters_table() -> Dict:
    """
    Retorna tabela completa de parâmetros por ciclo
    Para referência e validação
    """
    return {
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

def get_cycle_permissions(cycle_info: Dict) -> Dict:
    """Retorna permissões baseadas no ciclo"""
    cycle = cycle_info["cycle"]
    
    permissions = {
        "BOTTOM": {
            "allow_buy": True,
            "allow_sell": False,
            "priority": "maxima",
            "bias": "acumular",
            "urgency": "alta"
        },
        "ACUMULAÇÃO": {
            "allow_buy": True,
            "allow_sell": False, 
            "priority": "alta",
            "bias": "comprar",
            "urgency": "alta"
        },
        "BULL_INICIAL": {
            "allow_buy": True,
            "allow_sell": False,
            "priority": "media",
            "bias": "seletivo",
            "urgency": "media"
        },
        "BULL_MADURO": {
            "allow_buy": True,
            "allow_sell": True,
            "priority": "baixa_compra",
            "bias": "realizar_parcial", 
            "urgency": "baixa"
        },
        "EUFORIA_TOPO": {
            "allow_buy": False,
            "allow_sell": True,
            "priority": "maxima_venda",
            "bias": "realizar",
            "urgency": "critica"
        }
    }
    
    return permissions.get(cycle, {
        "allow_buy": True,
        "allow_sell": True,
        "priority": "media", 
        "bias": "neutro",
        "urgency": "baixa"
    })

def validate_cycle_consistency(score: float, mvrv: float) -> Dict:
    """
    Valida consistência entre Score e MVRV
    Detecta divergências importantes
    """
    
    # Faixas esperadas
    score_ranges = {
        "BOTTOM": (0, 20),
        "ACUMULAÇÃO": (20, 40), 
        "BULL_INICIAL": (40, 60),
        "BULL_MADURO": (60, 80),
        "EUFORIA_TOPO": (80, 100)
    }
    
    mvrv_ranges = {
        "BOTTOM": (0, 0.8),
        "ACUMULAÇÃO": (0.8, 1.2),
        "BULL_INICIAL": (1.2, 2.0), 
        "BULL_MADURO": (2.0, 3.0),
        "EUFORIA_TOPO": (3.0, 10.0)
    }
    
    # Determinar ciclo por cada métrica
    score_cycle = None
    mvrv_cycle = None
    
    for cycle, (min_val, max_val) in score_ranges.items():
        if min_val <= score <= max_val:
            score_cycle = cycle
            break
    
    for cycle, (min_val, max_val) in mvrv_ranges.items():
        if min_val <= mvrv <= max_val:
            mvrv_cycle = cycle
            break
    
    # Verificar consistência
    consistent = score_cycle == mvrv_cycle
    
    return {
        "consistent": consistent,
        "score_cycle": score_cycle,
        "mvrv_cycle": mvrv_cycle,
        "divergence": None if consistent else f"Score indica {score_cycle}, MVRV indica {mvrv_cycle}",
        "priority_cycle": score_cycle  # Score tem prioridade
    }