# app/services/v3/dash_main/execucao_tatica_service.py

import logging
from typing import Dict, Any
from .utils.gate_system_utils import aplicar_gate_system
from .utils.setup_detector_utils import identificar_setup_4h
from .utils.tecnicos_utils import obter_dados_tecnicos_4h
from .utils.helpers.comprar_helper import processar_estrategia_compra
from .utils.helpers.vender_helper import processar_estrategia_venda
from .utils.helpers.stop_helper import processar_estrategia_stop

logger = logging.getLogger(__name__)

def executar_execucao_tatica(dados_mercado: Dict, dados_risco: Dict, dados_alavancagem: Dict) -> Dict[str, Any]:
    """
    CAMADA 4: Execução Tática - Gate System + Setup Detection + Estratégia
    
    Args:
        dados_mercado: Resultados da camada 1 (scores, ciclo)
        dados_risco: Resultados da camada 2 (health_factor, score)
        dados_alavancagem: Resultados da camada 3 (alavancagem, status)
    
    Returns:
        Dict com 'tecnicos' e 'estrategia'
    """
    try:
        logger.info("🎯 Executando Camada 4: Execução Tática")
        
        # 1. DADOS TÉCNICOS 4H (RSI, EMA144, distância)
        logger.info("📊 Coletando dados técnicos 4H...")
        tecnicos = obter_dados_tecnicos_4h()
        logger.info(f"✅ Técnicos 4H: RSI={tecnicos['rsi']}, EMA_dist={tecnicos['ema_144_distance']}%")
        
        # 2. GATE SYSTEM (4 validações + overrides especiais)
        logger.info("🚪 Aplicando Gate System...")
        gate_result = aplicar_gate_system(dados_mercado, dados_risco, dados_alavancagem)
        logger.info(f"🚪 Gate: {gate_result['status']} - {gate_result['motivo']}")
        
        # 3. IDENTIFICAÇÃO SETUP 4H (se gate permitir)
        logger.info("🔍 Identificando setup 4H...")
        setup_info = identificar_setup_4h(tecnicos, gate_result)
        logger.info(f"🎯 Setup: {setup_info['setup']} - Força: {setup_info['forca']}")
        
        # 4. DECISÃO ESTRATÉGICA FINAL
        logger.info("⚡ Processando decisão estratégica...")
        estrategia = _processar_decisao_final(setup_info, gate_result, dados_alavancagem)
        logger.info(f"🎯 Decisão: {estrategia['decisao']} - Urgência: {estrategia['urgencia']}")
        
        return {
            "tecnicos": tecnicos,
            "estrategia": estrategia
        }
        
    except Exception as e:
        logger.error(f"❌ Erro Camada 4 Execução Tática: {str(e)}")
        raise Exception(f"Execução Tática falhou: {str(e)}")

def _processar_decisao_final(setup_info: Dict, gate_result: Dict, dados_alavancagem: Dict) -> Dict:
    """Processa decisão final baseada em setup, gate e situação alavancagem"""
    try:
        # OVERRIDE: Proteções absolutas
        if gate_result['override_especial']:
            return gate_result['estrategia_override']
        
        # BLOQUEADO: Gate system falhou
        if not gate_result['liberado']:
            return {
                "decisao": "BLOQUEADO",
                "setup_4h": "NAO_IDENTIFICADO", 
                "urgencia": "alta",
                "justificativa": gate_result['motivo']
            }
        
        # AJUSTAR ALAVANCAGEM: Prioridade sobre setup
        if dados_alavancagem.get('status') == 'deve_reduzir':
            return {
                "decisao": "AJUSTAR_ALAVANCAGEM",
                "setup_4h": setup_info['setup'],
                "urgencia": "alta", 
                "justificativa": f"Alavancagem no limite: {dados_alavancagem.get('atual', 0):.1f}x >= {dados_alavancagem.get('permitida', 0):.1f}x"
            }
        
        # SETUP IDENTIFICADO: Processar estratégia de compra
        if setup_info['setup'] != 'NENHUM':
            return processar_estrategia_compra(setup_info, dados_alavancagem)
        
        # AGUARDAR: Nenhum setup identificado
        return {
            "decisao": "AGUARDAR",
            "setup_4h": "NENHUM",
            "urgencia": "baixa",
            "justificativa": "Aguardando setup favorável"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro decisão final: {str(e)}")
        raise Exception(f"Falha decisão estratégica: {str(e)}")