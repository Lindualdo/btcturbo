# app/services/utils/helpers/matriz_tatica_helper.py

import logging


# Matriz EMA144/RSI - Decisões Táticas - Atualização 12/06 - Claude - Especialista Analise

MATRIZ_BASICA = [
    # Realizações
    {"id": 2,"ema_min": 20, "ema_max": 999, "rsi_min": 70, "rsi_max": 100, 
     "acao": "REALIZAR", "tamanho": 40, "justificativa": "Extremo sobrecomprado"},
    
    {"id": 2,"ema_min": 15, "ema_max": 20, "rsi_min": 65, "rsi_max": 100, 
     "acao": "REALIZAR", "tamanho": 25, "justificativa": "Esticado com RSI alto"},
    
    {"id": 3,"ema_min": 10, "ema_max": 15, "rsi_min": 70, "rsi_max": 100, 
     "acao": "REALIZAR", "tamanho": 15, "justificativa": "Início sobrecompra"},
    
    {"id": 3,"ema_min": 10, "ema_max": 15, "rsi_min": 55, "rsi_max": 65, 
    "acao": "REALIZAR", "tamanho": 10, "justificativa": "Moderadamente esticado"},

    # Compras
    {"id": 4,"ema_min": -999, "ema_max": -10, "rsi_min": 0, "rsi_max": 30, 
     "acao": "ADICIONAR", "tamanho": 75, "justificativa": "Capitulação"},
    
    {"id": 5,"ema_min": -10, "ema_max": -5, "rsi_min": 0, "rsi_max": 45, 
     "acao": "ADICIONAR", "tamanho": 35, "justificativa": "Desconto + oversold"},
    
    {"id": 6,"ema_min": -5, "ema_max": 5, "rsi_min": 20, "rsi_max": 40, 
     "acao": "ADICIONAR", "tamanho": 20, "justificativa": "Pullback saudável"},
    
    # Holds (default)
    {"id":7,"ema_min": -5, "ema_max": 10, "rsi_min": 40, "rsi_max": 70, 
     "acao": "HOLD", "tamanho": 0, "justificativa": "Zona neutra"}
]

def encontrar_acao_tatica(ema_distance: float, rsi_diario: float) -> dict:
    """Encontra ação na matriz tática"""
    for regra in MATRIZ_BASICA:
        ema_ok = regra["ema_min"] <= ema_distance <= regra["ema_max"]
        rsi_ok = regra["rsi_min"] <= rsi_diario <= regra["rsi_max"]
        
        if ema_ok and rsi_ok:
            return regra
    
    # Fallback: HOLD se não encontrar
    return {
        "acao": "HOLD",
        "tamanho": 0,
        "justificativa": "Condições não mapeadas - aguardar",
        "ema_min": ema_distance,
        "ema_max": ema_distance,
        "rsi_min": rsi_diario,
        "rsi_max": rsi_diario,
        "id_cenario": 0
    }

def calcular_score_tatico(acao: str, tamanho: int, ema_distance: float, rsi_diario: float) -> float:
    """Calcula score da oportunidade tática (0-100)"""
    # Score base por ação
    if acao == "ADICIONAR":
        base_score = 70 + (tamanho * 0.3)
    elif acao == "REALIZAR":
        base_score = 60 + (tamanho * 0.2)
    else:  # HOLD
        base_score = 50
    
    # Ajustes por contexto
    if acao == "ADICIONAR":
        if rsi_diario < 30:
            base_score += 10
        if ema_distance < -15:
            base_score += 10
    elif acao == "REALIZAR":
        if rsi_diario > 70:
            base_score += 10
        if ema_distance > 20:
            base_score += 10
    
    return min(100, max(0, base_score))