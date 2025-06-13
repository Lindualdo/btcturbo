# app/services/utils/helpers/v2/dashboard_home/validation_gates.py

import logging
from typing import Dict

logger = logging.getLogger(__name__)

def apply_protection_gates(data: Dict) -> Dict:
    """
    Aplica gates de proteção (Gate System da documentação)
    
    Gate System:
    1. CICLO PERMITE?
    2. RISCO OK? (Score > 40)
    3. HEALTH FACTOR OK? (HF > 1.2)
    4. TEM MARGEM?
    
    Returns:
        Dict com ação de proteção ou None se passou
    """
    try:
        logger.info("🛡️ Aplicando gates de proteção...")
        
        # Gate 1: Health Factor Crítico
        hf_result = _check_health_factor_gate(data)
        if hf_result["action_required"]:
            return hf_result
        
        # Gate 2: Score de Risco
        risk_result = _check_risk_score_gate(data)
        if risk_result["action_required"]:
            return risk_result
        
        # Gate 3: Alavancagem no Limite
        leverage_result = _check_leverage_gate(data)
        if leverage_result["action_required"]:
            return leverage_result
        
        # Gate 4: Capital Livre
        capital_result = _check_capital_gate(data)
        if capital_result["action_required"]:
            return capital_result
        
        logger.info("✅ Todos os gates passaram - prosseguir com matriz normal")
        return {"action_required": False}
        
    except Exception as e:
        logger.error(f"❌ Erro nos gates: {str(e)}")
        return {
            "action_required": True,
            "decision": "HOLD_ERRO",
            "justificativa": f"Erro na validação: {str(e)}",
            "urgencia": "critica"
        }

def _check_health_factor_gate(data: Dict) -> Dict:
    """
    Gate Health Factor: HF < 1.2 → Reduzir 50-80%
    """
    hf = data["health_factor"]
    
    if hf < 1.2:
        reducao_percent = 80 if hf < 1.1 else 50
        return {
            "action_required": True,
            "decision": f"REDUZIR_{reducao_percent}%",
            "justificativa": f"Health Factor crítico: {hf:.2f} < 1.2",
            "urgencia": "critica",
            "tipo_protecao": "health_factor"
        }
    
    return {"action_required": False}

def _check_risk_score_gate(data: Dict) -> Dict:
    """
    Gate Risco: Score < 40 → Reduzir 50%
    """
    score_risco = data["score_risco"]
    
    if score_risco < 40:
        return {
            "action_required": True,
            "decision": "REDUZIR_50%",
            "justificativa": f"Score de risco baixo: {score_risco:.1f} < 40",
            "urgencia": "alta",
            "tipo_protecao": "score_risco"
        }
    
    return {"action_required": False}

def _check_leverage_gate(data: Dict) -> Dict:
    """
    Gate Alavancagem: Atual >= Permitida → Ajustar primeiro
    """
    atual = data["alavancagem_atual"]
    permitida = data["alavancagem_permitida"]
    
    if atual >= permitida:
        return {
            "action_required": True,
            "decision": "AJUSTAR_ALAVANCAGEM",
            "justificativa": f"Alavancagem no limite: {atual:.1f}x >= {permitida:.1f}x",
            "urgencia": "alta",
            "tipo_protecao": "alavancagem_limite"
        }
    
    return {"action_required": False}

def _check_capital_gate(data: Dict) -> Dict:
    """
    Gate Capital: Capital livre < 5% → Bloqueado
    """
    valor_disponivel = data["valor_disponivel"]
    posicao_total = data.get("posicao_total", 10000)  # fallback
    
    # Calcular percentual de capital livre
    if posicao_total > 0:
        percent_livre = (valor_disponivel / posicao_total) * 100
        
        if percent_livre < 5:
            return {
                "action_required": True,
                "decision": "BLOQUEADO_CAPITAL",
                "justificativa": f"Capital livre insuficiente: {percent_livre:.1f}% < 5%",
                "urgencia": "media",
                "tipo_protecao": "capital_insuficiente"
            }
    
    return {"action_required": False}

def check_flash_crash_override(data: Dict) -> Dict:
    """
    Override especial para Flash Crash (queda > 25%)
    """
    ema_distance = data["ema_distance"]
    
    # Flash crash: muito abaixo da EMA144
    if ema_distance < -25:
        return {
            "action_required": True,
            "decision": "OPORTUNIDADE_CRASH",
            "justificativa": f"Flash crash detectado: {ema_distance:.1f}% abaixo EMA144",
            "urgencia": "maxima",
            "tipo_protecao": "oportunidade_extrema"
        }
    
    return {"action_required": False}

def check_extreme_opportunity_override(data: Dict) -> Dict:
    """
    Override para oportunidades raras (MVRV < 0.7 + RSI < 25)
    """
    mvrv = data["mvrv"]
    rsi = data["rsi_diario"]
    
    if mvrv < 0.7 and rsi < 25:
        return {
            "action_required": True,
            "decision": "ALL_IN_HISTORICO",
            "justificativa": f"Oportunidade histórica: MVRV {mvrv:.2f} + RSI {rsi:.1f}",
            "urgencia": "maxima",
            "tipo_protecao": "oportunidade_historica"
        }
    
    return {"action_required": False}