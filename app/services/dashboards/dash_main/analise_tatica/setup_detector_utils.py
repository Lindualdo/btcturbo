import logging
from typing import Dict, Any
from .setups.oversold_extremo import detectar_oversold_extremo
from .setups.pullback_tendencia import detectar_pullback_tendencia
from .setups.teste_suporte import detectar_teste_suporte
from .setups.rompimento_resistencia import detectar_rompimento

logger = logging.getLogger(__name__)

def identificar_setup() -> Dict[str, Any]:
    """
    Orquestrador de Setups - testa em ordem de prioridade
    
    Returns:
        Dict com setup identificado ou NENHUM
    """
    try:
        logger.info("🔍 Orquestrando detecção de setups...")
        
        # Ordem de prioridade (para no primeiro encontrado)
        setups = [
            ("OVERSOLD_EXTREMO", detectar_oversold_extremo),
            ("PULLBACK_TENDENCIA", detectar_pullback_tendencia),
            ("TESTE_SUPORTE", detectar_teste_suporte),
            ("ROMPIMENTO", detectar_rompimento)
        ]
        
        for setup_nome, setup_func in setups:
            logger.info(f"🔍 Testando setup: {setup_nome}")
            
            try:
                result = setup_func()
                
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
        return _setup_nenhum("Condições não atendidas")
        
    except Exception as e:
        logger.error(f"❌ Erro orquestrador setups: {str(e)}")
        return _setup_nenhum(f"Erro orquestrador: {str(e)}")

def _setup_nenhum(motivo: str) -> Dict[str, Any]:
    """Retorna setup NENHUM com motivo"""
    return {
        "encontrado": False,
        "setup": "NENHUM",
        "forca": "nenhuma",
        "tamanho_posicao": 0,
        "dados_tecnicos": {},
        "detalhes": motivo
    }