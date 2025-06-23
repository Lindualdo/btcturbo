# source: app/services/dashboards/dash_main/gate_system_utils.py

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def aplicar_gate_system(dados_mercado: Dict, dados_risco: Dict, dados_alavancagem: Dict) -> Dict[str, Any]:
    """
    Gate System: 4 Validações + Overrides Especiais
    
    Validações (todas devem passar):
    1. Score Risco >= 50
    2. Score Mercado >= 40  
    3. Health Factor >= 1.5
    4. Margem disponível >= 5%
    
    Overrides Especiais (ignoram tudo):
    - HF < 1.2 → REDUZIR 50-80%
    - Score Risco < 30 → REDUZIR 50%
    - Flash Crash > 25% → AVALIAR
    """
    try:
        logger.info("🚪 Iniciando Gate System...")
        
        # EXTRAIR DADOS
        score_risco = dados_risco.get('score', 0)
        score_mercado = dados_mercado.get('score_mercado', 0)
        health_factor = dados_risco.get('health_factor', 0)
        margem_disponivel = dados_alavancagem.get('valor_disponivel', 0)
        posicao_total = dados_alavancagem.get('posicao_total', 1)  # Evitar divisão por zero
        
        # será implementando depois de forma mais simples
        
        liberado = True
        motivo  = "Aprovado"
        if liberado:
            logger.info("✅ Gate System: LIBERADO para operação")
        else:
            logger.warning(f"🚫 Gate System: BLOQUEADO - {motivo}")
        
        return {
            "liberado": liberado,
            "status": "LIBERADO" if liberado else "BLOQUEADO",
            "motivo": motivo,
            "override_especial": False,
            "validacoes": validacoes
        }
        
    except Exception as e:
        logger.error(f"❌ Erro Gate System: {str(e)}")
        raise Exception(f"Gate System falhou: {str(e)}")

def _verificar_overrides_especiais(health_factor: float, score_risco: float) -> Dict[str, Any]:
    """Verifica proteções absolutas que ignoram todas as outras regras"""
    
    # OVERRIDE 1: Health Factor crítico
    if health_factor < 1.2:
        return {
            "ativo": True,
            "liberado": False,
            "status": "OVERRIDE_HF_CRITICO",
            "motivo": f"Health Factor crítico: {health_factor:.2f} < 1.2",
            "override_especial": True,
            "estrategia_override": {
                "decisao": "REDUZIR_URGENTE",
                "setup_4h": "PROTECAO_HF",
                "urgencia": "critica",
                "justificativa": f"Health Factor crítico ({health_factor:.2f}). Reduzir 50-80% posição imediatamente"
            }
        }
    
    # OVERRIDE 2: Score Risco crítico  
    if score_risco < 30:
        return {
            "ativo": True,
            "liberado": False,
            "status": "OVERRIDE_RISCO_CRITICO", 
            "motivo": f"Score Risco crítico: {score_risco} < 30",
            "override_especial": True,
            "estrategia_override": {
                "decisao": "REDUZIR_RISCO",
                "setup_4h": "PROTECAO_RISCO",
                "urgencia": "critica",
                "justificativa": f"Score Risco crítico ({score_risco}). Reduzir 50% posição por segurança"
            }
        }
    
    # TODO: OVERRIDE 3 - Flash Crash detection (implementar futuramente)
    # if flash_crash_percent > 25:
    #     return override_flash_crash()
    
    return {"ativo": False}

def _executar_validacoes_gate(score_risco: float, score_mercado: float, health_factor: float, margem_percent: float) -> Dict[str, bool]:
    """Executa as 4 validações do Gate System"""
    
    validacoes = {
        "score_risco_ok": score_risco >= 50,
        "score_mercado_ok": score_mercado >= 40,
        "health_factor_ok": health_factor >= 1.5,
        "margem_disponivel_ok": margem_percent >= 5.0
    }
    
    # Log individual de cada validação
    logger.info(f"🔍 Gate 1 - Score Risco >= 50: {score_risco} ({'✅' if validacoes['score_risco_ok'] else '❌'})")
    logger.info(f"🔍 Gate 2 - Score Mercado >= 40: {score_mercado} ({'✅' if validacoes['score_mercado_ok'] else '❌'})")
    logger.info(f"🔍 Gate 3 - Health Factor >= 1.5: {health_factor:.2f} ({'✅' if validacoes['health_factor_ok'] else '❌'})")
    logger.info(f"🔍 Gate 4 - Margem >= 5%: {margem_percent:.1f}% ({'✅' if validacoes['margem_disponivel_ok'] else '❌'})")
    
    return validacoes

def _gerar_motivo_gate(validacoes: Dict[str, bool]) -> str:
    """Gera motivo baseado nas validações que falharam"""
    
    if all(validacoes.values()):
        return "Todas validações passaram"
    
    motivos = []
    if not validacoes['score_risco_ok']:
        motivos.append("Score Risco < 50")
    if not validacoes['score_mercado_ok']:
        motivos.append("Score Mercado < 40")
    if not validacoes['health_factor_ok']:
        motivos.append("Health Factor < 1.5")
    if not validacoes['margem_disponivel_ok']:
        motivos.append("Margem < 5%")
    
    return " | ".join(motivos)