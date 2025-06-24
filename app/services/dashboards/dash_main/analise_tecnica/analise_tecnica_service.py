# app/services/dashboards/dash_main/analise_tecnica/analise_tecnica_service.py

import logging
from typing import Dict, Any
from .gate_system_utils import aplicar_gate_system
from .setup_detector_utils import identificar_setup

logger = logging.getLogger(__name__)

def executar_analise(dados_mercado: Dict, dados_risco: Dict, dados_alavancagem: Dict) -> Dict[str, Any]:
    """
    CAMADA 4: Execução Tática - Controlador principal
    
    Fluxo:
    1. Gate System (mockado v1.5.4)
    2. Se liberado → identifica setup
    3. Retorna dados técnicos + estratégia
    
    Args:
        dados_mercado: Dados da análise de mercado
        dados_risco: Dados da análise de risco  
        dados_alavancagem: Dados da análise de alavancagem
    
    Returns:
        Dict com dados técnicos e estratégia
    """
    try:
        logger.info("🎯 Executando Camada 4: Execução Tática")
        
        # 1. GATE SYSTEM (mockado v1.5.4)
        logger.info("🚪 Aplicando Gate System...")
        gate_result = aplicar_gate_system(dados_mercado, dados_risco, dados_alavancagem)
        logger.info(f"🚪 Gate: {gate_result['status']} - {gate_result['motivo']}")
        
        # 2. SE GATE BLOQUEADO → RETORNA BLOQUEADO
        if not gate_result['liberado']:
            logger.warning("🚫 Gate bloqueado - execução interrompida")
            return _retornar_bloqueado(gate_result['motivo'])
        
        # 3. IDENTIFICAR SETUP
        logger.info("🔍 Identificando setup...")
        setup_result = identificar_setup()
        
        # 4. PROCESSAR RESULTADO
        if setup_result.get('encontrado', False):
            setup_nome = setup_result.get('setup', 'DESCONHECIDO')
            forca = setup_result.get('forca', 'N/A')
            logger.info(f"✅ Setup {setup_nome} identificado - Força: {forca}")
        else:
            setup_nome = setup_result.get('setup', 'NENHUM')
            logger.info(f"❌ {setup_nome}")
        
        # 5. RETORNAR RESULTADO COMPLETO
        return {
            "tecnicos": setup_result.get('dados_tecnicos', {}),
            "estrategia": setup_result.get('estrategia', _estrategia_erro("Setup sem estratégia"))
        }
        
    except Exception as e:
        logger.error(f"❌ Erro Camada 4 Execução Tática: {str(e)}")
        return _retornar_erro(str(e))

def _retornar_bloqueado(motivo: str) -> Dict[str, Any]:
    """Retorna resultado quando gate system bloqueia execução"""
    return {
        "tecnicos": {},
        "estrategia": {
            "decisao": "BLOQUEADO",
            "setup": "NAO_IDENTIFICADO",
            "urgencia": "alta",
            "justificativa": f"Gate bloqueado: {motivo}"
        }
    }

def _retornar_erro(erro: str) -> Dict[str, Any]:
    """Retorna resultado quando ocorre erro na execução"""
    return {
        "tecnicos": {},
        "estrategia": {
            "decisao": "ERRO",
            "setup": "ERRO",
            "urgencia": "alta",
            "justificativa": f"Erro execução tática: {erro}"
        }
    }

def _estrategia_erro(mensagem: str) -> Dict[str, str]:
    """Estratégia padrão para casos de erro"""
    return {
        "decisao": "ERRO",
        "setup": "ERRO",
        "urgencia": "alta",
        "justificativa": mensagem
    }