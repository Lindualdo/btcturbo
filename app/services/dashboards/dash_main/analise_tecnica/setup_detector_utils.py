# app/services/dashboards/dash_main/analise_tecnica/setup_detector_utils.py

import logging
from typing import Dict, Any
from ..helpers.analise_tecnica_helper import get_todos_dados_tecnicos
from .setups_compra.oversold_extremo import detectar_oversold_extremo
from .setups_compra.pullback_tendencia import detectar_pullback_tendencia
from .setups_compra.teste_suporte import detectar_teste_suporte
from .setups_compra.rompimento_resistencia import detectar_rompimento
from .setups_compra.cruzamento_medias import detectar_cruzamento_medias

logger = logging.getLogger(__name__)

def identificar_setup() -> Dict[str, Any]:
    """
    Orquestrador de setups - busca dados técnicos e testa por prioridade
    
    Returns:
        Dict com setup identificado ou NENHUM
    """
    try:
        logger.info("🔍 Iniciando identificação de setups...")
        
        # 1. BUSCAR DADOS TÉCNICOS CONSOLIDADOS
        dados_tecnicos = get_todos_dados_tecnicos()
        logger.info("📊 Dados técnicos obtidos com sucesso")
        
        # 2. MATRIZ DE SETUPS POR PRIORIDADE
        setups = [
            ("OVERSOLD_EXTREMO", detectar_oversold_extremo),
            ("PULLBACK_TENDENCIA", detectar_pullback_tendencia),
            ("TESTE_SUPORTE", detectar_teste_suporte),
            ("ROMPIMENTO", detectar_rompimento),
            ("CRUZAMENTO_MEDIAS", detectar_cruzamento_medias)
        ]
        
        # 3. TESTAR SETUPS EM ORDEM (para no primeiro encontrado)
        for setup_nome, setup_func in setups:
            logger.info(f"🔍 Testando setup: {setup_nome}")
            
            try:
                resultado = setup_func(dados_tecnicos)
                
                if resultado.get('encontrado', False):
                    logger.info(f"✅ Setup {setup_nome} IDENTIFICADO - Força: {resultado.get('forca', 'N/A')}")
                    return resultado
                else:
                    logger.info(f"⚠️ Setup {setup_nome} não identificado")
                    
            except Exception as e:
                logger.error(f"❌ Erro ao testar setup {setup_nome}: {str(e)}")
                continue
        
        # 4. NENHUM SETUP ENCONTRADO
        logger.info("⚠️ Nenhum setup identificado")
        return _retornar_nenhum_setup(dados_tecnicos)
        
    except Exception as e:
        logger.error(f"❌ Erro orquestrador setups: {str(e)}")
        return _retornar_erro_setup(str(e))

def _retornar_nenhum_setup(dados_tecnicos: Dict) -> Dict[str, Any]:
    """Retorna resultado quando nenhum setup é identificado"""
    return {
        "encontrado": False,
        "setup": "NENHUM",
        "forca": "nenhuma",
        "tamanho_posicao": 0,
        "dados_tecnicos": dados_tecnicos,
        "estrategia": {
            "decisao": "AGUARDAR",
            "setup": "NENHUM",
            "urgencia": "baixa",
            "justificativa": "Nenhum setup identificado - aguardando condições favoráveis"
        }
    }

def _retornar_erro_setup(erro: str) -> Dict[str, Any]:
    """Retorna resultado quando ocorre erro na identificação"""
    return {
        "encontrado": False,
        "setup": "NENHUM",
        "forca": "nenhuma",
        "tamanho_posicao": 0,
        "dados_tecnicos": {},
        "estrategia": {
            "decisao": "ERRO",
            "setup": "NENHUM",
            "urgencia": "alta",
            "justificativa": f"Erro na identificação: {erro}"
        }
    }