
import logging
from typing import Dict, Any
from .gate_system_utils import aplicar_gate_system
from .setup_detector_utils import identificar_setup
from .comprar_helper import processar_estrategia_compra

logger = logging.getLogger(__name__)

def executar_analise(dados_mercado: Dict, dados_risco: Dict, dados_alavancagem: Dict) -> Dict[str, Any]:
    """
    CAMADA 4: Executa Análise Tática
    
    Fluxo:
    1. Gate System (validações + alertas)
    2. Se bloqueado → para
    3. Se liberado → identifica setup
    4. Processa decisão final
    """
    try:
        logger.info("🎯 Executando Camada 4: Execução Tática")
        
        # 1. GATE SYSTEM (validações + alertas)
        logger.info("🚪 Aplicando Gate System...")
        gate_result = aplicar_gate_system(dados_mercado, dados_risco, dados_alavancagem)
        logger.info(f"🚪 Gate: {gate_result['status']} - {gate_result['motivo']}")
        
        # 2. SE GATE BLOQUEADO → PARA AQUI
        if not gate_result['liberado']:
            logger.warning("🚫 Gate bloqueado - execução interrompida")
            return {
                "tecnicos": {},
                "estrategia": {
                    "decisao": "BLOQUEADO",
                    "setup": "NAO_IDENTIFICADO",
                    "urgencia": "alta",
                    "justificativa": gate_result['motivo']
                }
            }
        
        # 3. IDENTIFICAR SETUP
        logger.info("🔍 Identificando setup...")
        setup_info = identificar_setup()
        logger.info(f"🎯 Setup: {setup_info['setup']} - Encontrado: {setup_info.get('encontrado', False)}")
        
        # 4. PROCESSAR DECISÃO FINAL
        logger.info("⚡ Processando decisão estratégica...")
        estrategia = _processar_decisao_final(setup_info)
        logger.info(f"🎯 Decisão: {estrategia['decisao']} - Urgência: {estrategia['urgencia']}")
        
        return {
            "tecnicos": setup_info.get('dados_tecnicos', {}),
            "estrategia": estrategia
        }
        
    except Exception as e:
        logger.error(f"❌ Erro Camada 4 Execução Tática: {str(e)}")
        raise Exception(f"Execução Tática falhou: {str(e)}")

def _processar_decisao_final(setup_info: Dict) -> Dict:
    """Processa decisão final baseada em setup identificado"""
    try:
        # SETUP IDENTIFICADO: Processar estratégia de compra
        if setup_info.get('encontrado', False):
            return processar_estrategia_compra(setup_info)
        
        # AGUARDAR: Nenhum setup identificado
        return {
            "decisao": "AGUARDAR",
            "setup": "NENHUM",
            "urgencia": "baixa",
            "justificativa": "Aguardando setup favorável"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro decisão final: {str(e)}")
        raise Exception(f"Falha decisão estratégica: {str(e)}")