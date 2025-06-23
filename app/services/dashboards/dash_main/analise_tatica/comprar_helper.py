import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def processar_estrategia_compra(setup_info: Dict, dados_alavancagem: Dict) -> Dict[str, Any]:
    """
    Processa estratégia de COMPRA baseada no setup identificado
    
    Args:
        setup_info: Setup identificado pelos detectores
        dados_alavancagem: Não usado (validações no gate system)
    
    Returns:
        Dict com decisão de compra
    """
    try:
        setup_tipo = setup_info.get('setup', 'DESCONHECIDO')
        logger.info(f"💰 Processando estratégia COMPRA para setup: {setup_tipo}")
        
        # Dispatcher por tipo de setup
        if setup_tipo == "PULLBACK_TENDENCIA":
            return _processar_pullback_tendencia(setup_info)
        elif setup_tipo == "OVERSOLD_EXTREMO":
            return _processar_oversold_extremo(setup_info)
        elif setup_tipo == "TESTE_SUPORTE":
            return _processar_teste_suporte(setup_info)
        elif setup_tipo == "ROMPIMENTO":
            return _processar_rompimento(setup_info)
        else:
            return _estrategia_erro(f"Setup desconhecido: {setup_tipo}")
        
    except Exception as e:
        logger.error(f"❌ Erro estratégia compra: {str(e)}")
        return _estrategia_erro(f"Erro processar compra: {str(e)}")

def _processar_pullback_tendencia(setup_info: Dict) -> Dict[str, Any]:
    """Processa setup PULLBACK_TENDENCIA"""
    try:
        dados_tecnicos = setup_info.get('dados_tecnicos', {})
        rsi = dados_tecnicos.get('rsi', 0)
        ema_distance = dados_tecnicos.get('ema_144_distance', 0)
        forca = setup_info.get('forca', 'media')
        
        urgencia = "alta" if forca == "muito_alta" else "media"
        justificativa = f"Pullback tendência: RSI {rsi} + EMA dist {ema_distance:+.1f}%"
        
        return {
            "decisao": "COMPRAR",
            "setup": "PULLBACK_TENDENCIA",
            "urgencia": urgencia,
            "justificativa": justificativa
        }
        
    except Exception as e:
        logger.error(f"❌ Erro pullback tendência: {str(e)}")
        return _estrategia_erro(f"Erro pullback: {str(e)}")

def _processar_oversold_extremo(setup_info: Dict) -> Dict[str, Any]:
    """Processa setup OVERSOLD_EXTREMO"""
    try:
        dados_tecnicos = setup_info.get('dados_tecnicos', {})
        rsi = dados_tecnicos.get('rsi', 0)
        
        justificativa = f"Oversold extremo: RSI {rsi} < 30"
        
        return {
            "decisao": "COMPRAR",
            "setup": "OVERSOLD_EXTREMO",
            "urgencia": "critica",
            "justificativa": justificativa
        }
        
    except Exception as e:
        logger.error(f"❌ Erro oversold extremo: {str(e)}")
        return _estrategia_erro(f"Erro oversold: {str(e)}")

def _processar_teste_suporte(setup_info: Dict) -> Dict[str, Any]:
    """Processa setup TESTE_SUPORTE"""
    try:
        dados_tecnicos = setup_info.get('dados_tecnicos', {})
        ema_distance = dados_tecnicos.get('ema_144_distance', 0)
        
        justificativa = f"Teste suporte EMA144: dist {ema_distance:+.1f}%"
        
        return {
            "decisao": "COMPRAR",
            "setup": "TESTE_SUPORTE",
            "urgencia": "media",
            "justificativa": justificativa
        }
        
    except Exception as e:
        logger.error(f"❌ Erro teste suporte: {str(e)}")
        return _estrategia_erro(f"Erro teste suporte: {str(e)}")

def _processar_rompimento(setup_info: Dict) -> Dict[str, Any]:
    """Processa setup ROMPIMENTO"""
    try:
        dados_tecnicos = setup_info.get('dados_tecnicos', {})
        ema_distance = dados_tecnicos.get('ema_144_distance', 0)
        rsi = dados_tecnicos.get('rsi', 0)
        
        justificativa = f"Rompimento: EMA dist {ema_distance:+.1f}% + RSI {rsi}"
        
        return {
            "decisao": "COMPRAR",
            "setup": "ROMPIMENTO",
            "urgencia": "media",
            "justificativa": justificativa
        }
        
    except Exception as e:
        logger.error(f"❌ Erro rompimento: {str(e)}")
        return _estrategia_erro(f"Erro rompimento: {str(e)}")

def _estrategia_erro(mensagem: str) -> Dict[str, Any]:
    """Retorna estratégia de erro padronizada"""
    return {
        "decisao": "ERRO",
        "setup": "ERRO",
        "urgencia": "alta",
        "justificativa": mensagem
    }