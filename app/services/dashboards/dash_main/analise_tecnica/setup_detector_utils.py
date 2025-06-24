# app/services/dashboards/dash_main/analise_tatica/setup_detector_utils.py

import logging
from typing import Dict, Any
from .setups.oversold_extremo import detectar_oversold_extremo
from .setups.pullback_tendencia import detectar_pullback_tendencia
from .setups.teste_suporte import detectar_teste_suporte
from .setups.rompimento_resistencia import detectar_rompimento
from .setups.cruzamento_medias import detectar_cruzamento_medias
from ..helpers.analise_tecnica_helper import obter_dados_tecnicos

logger = logging.getLogger(__name__)

def identificar_setup() -> Dict[str, Any]:
    """
    Orquestrador de Setups - testa em ordem de prioridade
    
    Returns:
        Dict com setup identificado ou NENHUM
    """
    try:
        logger.info("🔍 Orquestrando detecção de setups...")
        
        # buscar todos os dados tencnicos para validar setuups (IMPLEMENTRA)
        # encadear todos os dados tecncicos até o data_buider (IMPLEMENTAR)
        dados_tecnicos_consolidados = obter_dados_tecnicos
        
        # Ordem de prioridade (para no primeiro encontrado
        setups = [
            ("OVERSOLD_EXTREMO", detectar_oversold_extremo),
            ("PULLBACK_TENDENCIA", detectar_pullback_tendencia),
            ("CRUZAMENTO_MEDIAS", detectar_cruzamento_medias),
            ("TESTE_SUPORTE", detectar_teste_suporte),
            ("ROMPIMENTO", detectar_rompimento)
        ]
        
        for setup_nome, setup_func in setups:
            logger.info(f"🔍 Testando setup: {setup_nome}")
            
            try:
                result = setup_func()

                # Captura dados técnicos do primeiro setup com dados reais
                if (not dados_tecnicos_consolidados and 
                    result.get('dados_tecnicos') and 
                    result.get('dados_tecnicos', {}).get('rsi', 0) > 0):
                    dados_tecnicos_consolidados = result['dados_tecnicos']
                
                # Captura dados EMAs do cruzamento se disponível
                if (not dados_tecnicos_consolidados and 
                    result.get('dados_tecnicos') and 
                    result.get('dados_tecnicos', {}).get('ema_17', 0) > 0):
                    dados_tecnicos_consolidados = result['dados_tecnicos']
                
                if result.get('encontrado', False):
                    logger.info(f"✅ Setup {setup_nome} IDENTIFICADO - Força: {result.get('forca', 'N/A')}")
                    return result
                else:
                    logger.info(f"❌ Setup {setup_nome} não identificado")
                    
            except Exception as e:
                logger.error(f"❌ Erro ao testar setup {setup_nome}: {str(e)}")
                continue
        
        # Nenhum setup identificado
        logger.info("❌ Nenhum setup identificado")
        logger.info(f"🔍 Dados consolidados: {dados_tecnicos_consolidados}")
        return _setup_nenhum("Condições não atendidas", dados_tecnicos_consolidados)
        
    except Exception as e:
        logger.error(f"❌ Erro orquestrador setups: {str(e)}")
        return _setup_nenhum(f"Erro orquestrador: {str(e)}", {})

def _setup_nenhum(motivo: str, dados_tecnicos: Dict = None) -> Dict[str, Any]:
    """Retorna setup NENHUM com motivo e dados técnicos consolidados"""
    return {
        "encontrado": False,
        "setup": "NENHUM",
        "forca": "nenhuma",
        "tamanho_posicao": 0,
        "dados_tecnicos": dados_tecnicos or {},
        "detalhes": motivo
    }