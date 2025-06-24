# app/services/dashboards/dash_main/analise_tecnica/gate_system_utils.py

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def aplicar_gate_system(dados_mercado: Dict, dados_risco: Dict, dados_alavancagem: Dict) -> Dict[str, Any]:
    """
    Gate System: Mockado v1.5.4 - sempre aprova
    
    Args:
        dados_mercado: Dados da análise de mercado
        dados_risco: Dados da análise de risco
        dados_alavancagem: Dados da análise de alavancagem
    
    Returns:
        Dict com status do gate (sempre liberado na v1.5.4)
    """
    try:
        logger.info("🚪 Aplicando Gate System (mockado v1.5.4)...")
        
        # TODO: Implementar validações reais v1.5.5+
        # - Score Risco >= 50
        # - Score Mercado >= 40
        # - Health Factor >= 1.5
        # - Margem disponível >= 5%
        
        # MOCKADO: sempre libera para testar arquitetura
        liberado = True
        motivo = "Aprovado (mockado v1.5.4)"
        
        logger.info(f"🚪 Gate Result: {'LIBERADO' if liberado else 'BLOQUEADO'} - {motivo}")
        
        return {
            "liberado": liberado,
            "status": "LIBERADO" if liberado else "BLOQUEADO", 
            "motivo": motivo,
            "override_especial": False,
            "versao": "mockado_v1.5.4"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro Gate System: {str(e)}")
        return {
            "liberado": False,
            "status": "ERRO",
            "motivo": f"Erro gate system: {str(e)}",
            "override_especial": False,
            "versao": "mockado_v1.5.4"
        }