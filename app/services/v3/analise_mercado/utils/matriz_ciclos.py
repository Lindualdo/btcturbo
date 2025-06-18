# app/services/v3/analise_mercado/utils/matriz_ciclos.py

import logging

logger = logging.getLogger(__name__)

def identificar_ciclo(score: float, mvrv: float, nupl: float) -> dict:
    """
    Identifica ciclo baseado na matriz de 18 cenários
    
    Aplica regras de prevalência:
    1. NUPL < 0 sempre zona de compra
    2. MVRV > 4 sempre zona de topo  
    3. Scores extremos prevalecem
    """
    
    # REGRA 1: NUPL < 0 - ZONA COMPRA EXTREMA (override tudo)
    if nupl < 0:
        return _ciclo_nupl_negativo(score)
    
    # REGRA 2: MVRV > 4 - ZONA TOPO (override exceto NUPL < 0)
    if mvrv > 4.0:
        return _ciclo_topo_mania()
    
    # REGRA 3: SCORES EXTREMOS (override faixas intermediárias)
    if score >= 90:
        return _ciclo_score_extremo_alto(mvrv)
    elif score <= 20:
        return _ciclo_score_extremo_baixo(mvrv)
    
    # MATRIZ NORMAL - sem overrides
    return _matriz_score_normal(score, mvrv, nupl)

def _ciclo_nupl_negativo(score: float) -> dict:
    """NUPL < 0 - zonas de compra histórica"""
    if score <= 20:
        return {
            "nome": "CAPITULAÇÃO",
            "caracteristicas": "Pânico total, fundos fechando",
            "estrategia": "All-in histórico",
            "confianca": 95,
            "override": "NUPL_NEGATIVO"
        }
    else:
        return {
            "nome": "BEAR PROFUNDO",
            "caracteristicas": "Desespero, mídia negativa", 
            "estrategia": "Acumular forte",
            "confianca": 90,
            "override": "NUPL_NEGATIVO"
        }

def _ciclo_topo_mania() -> dict:
    """MVRV > 4 - zona de topo"""
    return {
        "nome": "TOPO MANIA",
        "caracteristicas": "Euforia extrema, notícias mainstream",
        "estrategia": "Sair 80-100%",
        "confianca": 95,
        "override": "MVRV_EXTREMO"
    }

def _ciclo_score_extremo_alto(mvrv: float) -> dict:
    """Score >= 90 - condições extremas positivas"""
    if mvrv < 0.8:
        return {
            "nome": "REVERSÃO ÉPICA",
            "caracteristicas": "V-bottom histórico",
            "estrategia": "Compra máxima", 
            "confianca": 95,
            "override": "SCORE_EXTREMO"
        }
    else:
        return {
            "nome": "EUFORIA",
            "caracteristicas": "Parabólico, retail all-in",
            "estrategia": "Sair 50-80%",
            "confianca": 90,
            "override": "SCORE_EXTREMO"
        }

def _ciclo_score_extremo_baixo(mvrv: float) -> dict:
    """Score <= 20 - condições extremas negativas"""
    if mvrv < 1.0:
        return {
            "nome": "CAPITULAÇÃO",
            "caracteristicas": "Pânico total, fundos fechando",
            "estrategia": "All-in histórico",
            "confianca": 90,
            "override": "SCORE_EXTREMO"
        }
    else:
        return {
            "nome": "TOPO MANIA", 
            "caracteristicas": "Euforia extrema, notícias mainstream",
            "estrategia": "Sair 80-100%",
            "confianca": 85,
            "override": "SCORE_EXTREMO"
        }

def _matriz_score_normal(score: float, mvrv: float, nupl: float) -> dict:
    """Aplica matriz normal quando não há overrides"""
    
    if 80 <= score < 90:
        return _faixa_80_90(mvrv)
    elif 70 <= score < 80:
        return _faixa_70_80(mvrv)
    elif 60 <= score < 70:
        return _faixa_60_70(mvrv)
    elif 50 <= score < 60:
        return _faixa_50_60(mvrv)
    elif 40 <= score < 50:
        return _faixa_40_50(mvrv)
    elif 30 <= score < 40:
        return _faixa_30_40(mvrv)
    elif 20 <= score < 30:
        return _faixa_20_30(mvrv)
    else:
        return {
            "nome": "INDEFINIDO",
            "caracteristicas": "Condições atípicas",
            "estrategia": "Aguardar clareza",
            "confianca": 30
        }

def _faixa_80_90(mvrv: float) -> dict:
    """Score 80-90: BULL FORTE"""
    if mvrv < 1.0:
        return {
            "nome": "OPORTUNIDADE GERACIONAL",
            "caracteristicas": "Capitulação com reversão técnica",
            "estrategia": "All-in + Alavancagem",
            "confianca": 85
        }
    else:
        return {
            "nome": "BULL FORTE",
            "caracteristicas": "Momentum poderoso, notícias positivas",
            "estrategia": "Hold + Stops",
            "confianca": 80
        }

def _faixa_70_80(mvrv: float) -> dict:
    """Score 70-80: BULL CONFIRMADO"""
    if mvrv < 1.2:
        return {
            "nome": "NOVO CICLO",
            "caracteristicas": "Saindo de bear, reversão confirmada",
            "estrategia": "Alavancagem máxima",
            "confianca": 85
        }
    else:
        return {
            "nome": "BULL CONFIRMADO",
            "caracteristicas": "Tendência clara, FOMO inicial",
            "estrategia": "Hold + Comprar dips",
            "confianca": 80
        }

def _faixa_60_70(mvrv: float) -> dict:
    """Score 60-70: BULL INICIAL"""
    if mvrv < 1.8:
        return {
            "nome": "SAÍDA ACUMULAÇÃO",
            "caracteristicas": "Volume crescente, breakouts",
            "estrategia": "Posição completa",
            "confianca": 75
        }
    else:
        return {
            "nome": "BULL INICIAL", 
            "caracteristicas": "Rompimentos, otimismo crescente",
            "estrategia": "Comprar rallies",
            "confianca": 75
        }

def _faixa_50_60(mvrv: float) -> dict:
    """Score 50-60: NEUTRO"""
    if mvrv < 2.0:
        return {
            "nome": "NEUTRO",
            "caracteristicas": "Consolidação, baixa volatilidade", 
            "estrategia": "Aguardar sinal",
            "confianca": 65
        }
    else:
        return {
            "nome": "NEUTRO ALTA",
            "caracteristicas": "Indecisão com viés positivo",
            "estrategia": "Posição base",
            "confianca": 70
        }

def _faixa_40_50(mvrv: float) -> dict:
    """Score 40-50: ACUMULAÇÃO/CORREÇÃO"""
    if mvrv < 2.0:
        return {
            "nome": "ACUMULAÇÃO",
            "caracteristicas": "Lateralização, volume baixo",
            "estrategia": "Pequenas entradas",
            "confianca": 70
        }
    else:
        return {
            "nome": "CORREÇÃO BULL",
            "caracteristicas": "Pullback em tendência alta",
            "estrategia": "Comprar correção",
            "confianca": 75
        }

def _faixa_30_40(mvrv: float) -> dict:
    """Score 30-40: RECUPERAÇÃO/BULL TARDIO"""
    if mvrv < 1.5:
        return {
            "nome": "RECUPERAÇÃO",
            "caracteristicas": "Bear acabando, sentimento melhorando",
            "estrategia": "DCA conservador",
            "confianca": 70
        }
    else:
        return {
            "nome": "BULL TARDIO",
            "caracteristicas": "Ganância crescente, leverage alta",
            "estrategia": "Realizar gradual",
            "confianca": 75
        }

def _faixa_20_30(mvrv: float) -> dict:
    """Score 20-30: BEAR PROFUNDO/DISTRIBUIÇÃO"""
    if mvrv < 1.2:
        return {
            "nome": "BEAR PROFUNDO",
            "caracteristicas": "Desespero, mídia negativa",
            "estrategia": "Acumular forte",
            "confianca": 75
        }
    else:
        return {
            "nome": "DISTRIBUIÇÃO",
            "caracteristicas": "Smart money vendendo, retail comprando",
            "estrategia": "Realizar 60%+",
            "confianca": 80
        }