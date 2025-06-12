# app/services/utils/helpers/dashboard_home/fase_mercado_helper.py

FASES_MERCADO = {
    "bottom": {"mvrv_max": 1.0},
    "acumulacao": {"mvrv_min": 1.0, "mvrv_max": 2.0},
    "bull_medio": {"mvrv_min": 2.0, "mvrv_max": 3.0},
    "topo": {"mvrv_min": 3.0}
}

def identificar_fase_mercado(mvrv: float) -> str:
    """
    Identifica fase do mercado baseada no MVRV Z-Score
    
    Args:
        mvrv: Valor do MVRV Z-Score
    
    Returns:
        str: Fase do mercado (bottom, acumulacao, bull_medio, topo)
    """
    for fase, limites in FASES_MERCADO.items():
        mvrv_min = limites.get("mvrv_min", -999)
        mvrv_max = limites.get("mvrv_max", 999)
        
        if mvrv_min <= mvrv < mvrv_max:
            return fase
    
    return "indefinido"