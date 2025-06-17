# services/v3/gate_system.py
import logging

logger = logging.getLogger(__name__)

def apply_gate_system(data: dict) -> dict:
    """
    Gate system centralizado - Validações de proteção
    Conforme documentado: HF < 1.2, Score Risco < 40, Capital < 5%
    """
    try:
        logger.info("🛡️ Aplicando gate system...")
        
        gates_results = []
        
        # GATE 1: Health Factor crítico
        gate1 = _check_health_factor_gate(data["risco"])
        gates_results.append(gate1)
        
        # GATE 2: Score de risco baixo
        gate2 = _check_risk_score_gate(data["risco"])
        gates_results.append(gate2)
        
        # GATE 3: Capital livre insuficiente
        gate3 = _check_capital_gate(data["alavancagem"])
        gates_results.append(gate3)
        
        # GATE 4: Alavancagem excessiva
        gate4 = _check_leverage_gate(data["alavancagem"])
        gates_results.append(gate4)
        
        # Verificar se algum gate foi acionado
        blocked_gates = [g for g in gates_results if g["blocked"]]
        
        if blocked_gates:
            # Gate mais crítico (menor prioridade = mais crítico)
            critical_gate = min(blocked_gates, key=lambda x: x["priority"])
            
            logger.warning(f"🚨 Gate acionado: {critical_gate['name']}")
            
            return {
                "blocked": True,
                "reason": critical_gate["name"],
                "action": critical_gate["action"],
                "response": _generate_protection_response(critical_gate)
            }
        
        logger.info("✅ Gate system liberado")
        return {
            "blocked": False,
            "reason": None,
            "gates_checked": len(gates_results)
        }
        
    except Exception as e:
        logger.error(f"❌ Erro gate system: {str(e)}")
        return {
            "blocked": True,
            "reason": "ERRO_SISTEMA",
            "response": {
                "status": "error",
                "message": f"Erro no gate system: {str(e)}"
            }
        }

def _check_health_factor_gate(risco_data: dict) -> dict:
    """Gate 1: Health Factor < 1.2 → REDUZIR 50-80%"""
    hf = risco_data["health_factor"]
    
    if hf < 1.2:
        if hf < 1.1:
            reducao = 80
        else:
            reducao = 50
            
        return {
            "blocked": True,
            "name": "HEALTH_FACTOR_CRITICO",
            "priority": 1,  # Mais crítico
            "action": f"REDUZIR_{reducao}%",
            "value": hf,
            "threshold": 1.2
        }
    
    return {"blocked": False, "name": "HEALTH_FACTOR_OK"}

def _check_risk_score_gate(risco_data: dict) -> dict:
    """Gate 2: Score Risco < 40 → REDUZIR 50%"""
    score = risco_data["score"]
    
    if score < 40:
        return {
            "blocked": True,
            "name": "SCORE_RISCO_BAIXO",
            "priority": 2,
            "action": "REDUZIR_50%",
            "value": score,
            "threshold": 40
        }
    
    return {"blocked": False, "name": "SCORE_RISCO_OK"}

def _check_capital_gate(alav_data: dict) -> dict:
    """Gate 3: Capital Livre < 5% → BLOQUEADO"""
    capital_percent = alav_data["capital_livre_percent"]
    
    if capital_percent < 5:
        return {
            "blocked": True,
            "name": "CAPITAL_INSUFICIENTE",
            "priority": 3,
            "action": "BLOQUEADO",
            "value": capital_percent,
            "threshold": 5
        }
    
    return {"blocked": False, "name": "CAPITAL_OK"}

def _check_leverage_gate(alav_data: dict) -> dict:
    """Gate 4: Alavancagem >= Permitida → AJUSTAR"""
    atual = alav_data["alavancagem_atual"]
    permitida = alav_data["limite_max"]
    
    if atual >= permitida:
        return {
            "blocked": True,
            "name": "ALAVANCAGEM_EXCESSIVA",
            "priority": 4,
            "action": "AJUSTAR_PRIMEIRO",
            "value": atual,
            "threshold": permitida
        }
    
    return {"blocked": False, "name": "ALAVANCAGEM_OK"}

def _generate_protection_response(gate: dict) -> dict:
    """Gera resposta de proteção padronizada"""
    return {
        "status": "protection_activated",
        "gate_acionado": gate["name"],
        "acao_requerida": gate["action"],
        "data": {
            "header": {
                "status": "protecao_ativa",
                "btc_price": 105000.0,  # Mock
                "alavancagem_atual": gate.get("value", 0)
            },
            "estrategia": {
                "decisao": gate["action"],
                "justificativa": f"Gate {gate['name']}: {gate['value']} vs limite {gate['threshold']}",
                "urgencia": "critica"
            }
        }
    }