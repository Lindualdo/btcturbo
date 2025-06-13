# app/services/utils/helpers/v2/dashboard_home/decision_matrix.py

import logging
from typing import Dict

logger = logging.getLogger(__name__)

def apply_decision_matrix(cycle_info: Dict, setup_info: Dict, data: Dict) -> Dict:
    """
    Aplica matriz de decisão final baseada em Ciclo + Setup (tabela oficial)
    """
    try:
        cycle = cycle_info["cycle"]
        setup = setup_info["setup"]
        action = setup_info["action"]
        
        logger.info(f"🎯 Aplicando matriz: {cycle} + {setup} → {action}")
        
        # 1. VERIFICAR OVERRIDES ESPECIAIS PRIMEIRO
        override_result = _check_special_overrides(data)
        if override_result:
            return override_result
        
        # 2. APLICAR MATRIZ OFICIAL CICLO × SETUP
        decision = _get_official_matrix_decision(cycle, setup, action, data)
        
        # 3. APLICAR AJUSTES POR CONTEXTO
        final_decision = _apply_context_adjustments(decision, data)
        
        logger.info(f"✅ Decisão final: {final_decision['decision']} ({final_decision['size']}%)")
        
        return final_decision
        
    except Exception as e:
        logger.error(f"❌ Erro matriz decisão: {str(e)}")
        return {
            "decision": "HOLD_ERRO",
            "size": 0,
            "justificativa": f"Erro na matriz: {str(e)}",
            "urgencia": "baixa"
        }

def _check_special_overrides(data: Dict) -> Optional[Dict]:
    """
    Verifica overrides especiais que ignoram tudo
    """
    hf = data["health_factor"]
    score_risco = data["score_risco"]
    ema_distance = data["ema_distance"]
    mvrv = data["mvrv"]
    rsi = data["rsi_diario"]
    
    # PROTEÇÃO ABSOLUTA
    if hf < 1.3:
        return {
            "decision": "REDUZIR_80%",
            "size": 80,
            "justificativa": f"Health Factor crítico: {hf:.2f} < 1.3",
            "urgencia": "critica",
            "override": "protecao_absoluta"
        }
    
    if score_risco < 30:
        return {
            "decision": "FECHAR_TUDO",
            "size": 100,
            "justificativa": f"Score risco crítico: {score_risco:.1f} < 30",
            "urgencia": "critica", 
            "override": "protecao_absoluta"
        }
    
    if ema_distance < -20:  # Flash crash > 20%
        return {
            "decision": "AVALIAR_LIQUIDEZ",
            "size": 0,
            "justificativa": f"Flash crash detectado: {ema_distance:.1f}%",
            "urgencia": "critica",
            "override": "flash_crash"
        }
    
    # OPORTUNIDADES RARAS
    if mvrv < 0.5 and rsi < 20:
        return {
            "decision": "ALL_IN_HISTORICO", 
            "size": 100,
            "justificativa": f"Oportunidade histórica: MVRV {mvrv:.2f} + RSI {rsi:.1f}",
            "urgencia": "maxima",
            "override": "oportunidade_rara"
        }
    
    # TODO: Implementar outros overrides raros (ATH + correção, capitulação)
    
    return None

def _get_official_matrix_decision(cycle: str, setup: str, action: str, data: Dict) -> Dict:
    """
    Matriz oficial Ciclo × Setup conforme documentação
    """
    
    # BEAR
    if cycle == "BEAR":
        return {"decision": "IGNORAR", "size": 0, "priority": "nenhuma"}
    
    # ACUMULAÇÃO
    elif cycle == "ACUMULAÇÃO":
        if setup == "PULLBACK_TENDENCIA":
            return {"decision": "COMPRAR", "size": 12, "priority": "baixa"}  # 10-15%
        elif setup == "OVERSOLD_EXTREMO":
            return {"decision": "COMPRAR", "size": 20, "priority": "media"}
        else:
            return {"decision": "MONITORAR", "size": 0, "priority": "baixa"}
    
    # BULL INICIAL
    elif cycle == "BULL_INICIAL":
        if setup == "PULLBACK_TENDENCIA":
            return {"decision": "COMPRAR", "size": 35, "priority": "alta"}  # 30-40%
        elif setup == "ROMPIMENTO":
            return {"decision": "COMPRAR", "size": 25, "priority": "alta"}
        else:
            return {"decision": "MANTER", "size": 0, "priority": "media"}
    
    # BULL MADURO
    elif cycle == "BULL_MADURO":
        if setup == "PULLBACK_TENDENCIA":
            return {"decision": "COMPRAR", "size": 20, "priority": "media"}
        elif setup in ["RESISTENCIA", "EXAUSTAO"]:
            return {"decision": "REALIZAR", "size": 27, "priority": "alta"}  # 25-30%
        else:
            return {"decision": "MANTER_STOPS", "size": 0, "priority": "media"}
    
    # EUFORIA/TOPO
    elif cycle == "EUFORIA_TOPO":
        if action == "COMPRAR":
            return {"decision": "IGNORAR", "size": 0, "priority": "nenhuma"}
        elif action == "REALIZAR":
            return {"decision": "REALIZAR", "size": 35, "priority": "maxima"}  # 30-40%
        else:
            return {"decision": "REALIZAR_GRADUAL", "size": 20, "priority": "alta"}
    
    # Default
    else:
        return {"decision": "HOLD", "size": 0, "priority": "baixa"}

def _apply_context_adjustments(decision: Dict, data: Dict) -> Dict:
    """
    Aplica ajustes baseados no contexto atual
    """
    # Ajustar tamanho baseado em Health Factor
    hf_adjustment = _get_hf_adjustment(data["health_factor"])
    adjusted_size = int(decision["size"] * hf_adjustment)
    
    # Ajustar por score de risco
    risk_adjustment = _get_risk_adjustment(data["score_risco"])
    adjusted_size = int(adjusted_size * risk_adjustment)
    
    # Justificativa
    justificativa = _build_justification(decision, data)
    
    # Urgência
    urgencia = _determine_urgency(decision["priority"], data)
    
    return {
        "decision": decision["decision"],
        "size": max(0, min(adjusted_size, 50)),  # Cap em 50%
        "justificativa": justificativa,
        "urgencia": urgencia,
        "priority": decision["priority"],
        "adjustments": {
            "original_size": decision["size"],
            "hf_factor": hf_adjustment,
            "risk_factor": risk_adjustment
        }
    }

def _get_hf_adjustment(health_factor: float) -> float:
    """Ajuste baseado em Health Factor"""
    if health_factor > 2.0:
        return 1.2  # +20% se HF muito alto
    elif health_factor > 1.5:
        return 1.0  # Normal
    elif health_factor > 1.3:
        return 0.8  # -20% se HF médio
    else:
        return 0.5  # -50% se HF baixo

def _get_risk_adjustment(score_risco: float) -> float:
    """Ajuste baseado em Score de Risco"""
    if score_risco > 80:
        return 1.1  # +10% se risco muito baixo
    elif score_risco > 60:
        return 1.0  # Normal
    elif score_risco > 40:
        return 0.9  # -10% se risco médio
    else:
        return 0.6  # -40% se risco alto

def _build_justification(decision: Dict, data: Dict) -> str:
    """Constrói justificativa da decisão"""
    base_action = decision["decision"]
    size = decision["size"]
    
    if base_action == "COMPRAR":
        return f"Ciclo permite compras com setup favorável. Tamanho: {size}%"
    elif base_action == "REALIZAR":
        return f"Sinais de resistência/exaustão detectados. Realizar: {size}%"
    elif base_action == "HOLD":
        return "Aguardar setup mais claro ou melhores condições"
    elif base_action == "IGNORAR":
        return "Ciclo não permite compras. Focar em realizações"
    else:
        return "Decisão baseada em matriz de ciclo vs setup"

def _determine_urgency(priority: str, data: Dict) -> str:
    """Determina urgência baseada em prioridade e contexto"""
    if priority == "maxima":
        return "critica"
    elif priority == "alta":
        return "alta"
    elif priority == "media":
        return "media"
    else:
        return "baixa"