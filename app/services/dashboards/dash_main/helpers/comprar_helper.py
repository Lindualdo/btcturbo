# source: app/services/dashboards/dash_main/helpers/comprar_helper.py

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def processar_estrategia_compra(setup_info: Dict, dados_alavancagem: Dict) -> Dict[str, Any]:
    """
    Processa estratégia de COMPRA baseada no setup identificado
    
    Args:
        setup_info: Setup identificado (PULLBACK_TENDENCIA, TESTE_SUPORTE, etc.)
        dados_alavancagem: Situação atual de alavancagem
    
    Returns:
        Dict com decisão, setup, urgência e justificativa
    """
    try:
        logger.info(f"💰 Processando estratégia COMPRA para setup: {setup_info['setup']}")
        
        setup_nome = setup_info.get('setup', 'NENHUM')
        
        # SETUP ESPECÍFICOS
        if setup_nome == "OVERSOLD_EXTREMO":
            return _processar_oversold_extremo(setup_info, dados_alavancagem)
        
        elif setup_nome == "PULLBACK_TENDENCIA":
            return _processar_pullback_tendencia(setup_info, dados_alavancagem)
        
        elif setup_nome == "TESTE_SUPORTE":
            return _processar_teste_suporte(setup_info, dados_alavancagem)
        
        elif setup_nome == "ROMPIMENTO":
            return _processar_rompimento(setup_info, dados_alavancagem)
        
        else:
            logger.warning(f"⚠️ Setup não reconhecido: {setup_nome}")
            return _estrategia_aguardar("Setup não reconhecido")
        
    except Exception as e:
        logger.error(f"❌ Erro estratégia compra: {str(e)}")
        return _estrategia_erro(f"Erro processar compra: {str(e)}")

def _processar_oversold_extremo(setup_info: Dict, dados_alavancagem: Dict) -> Dict[str, Any]:
    """Processa setup OVERSOLD_EXTREMO (RSI < 30)"""
    try:
        rsi = setup_info['condicoes']['rsi']
        tamanho = setup_info['tamanho_posicao']
        
        # Verificar se tem margem para posição de 40%
        margem_disponivel = dados_alavancagem.get('valor_disponivel', 0)
        posicao_total = dados_alavancagem.get('posicao_total', 1)
        margem_percent = (margem_disponivel / posicao_total * 100) if posicao_total > 0 else 0
        
        if margem_percent >= 15:  # Margem suficiente para 40%
            urgencia = "muito_alta"
            justificativa = f"RSI extremo {rsi} < 30. Oportunidade rara - posição {tamanho}%"
        else:
            urgencia = "alta"
            justificativa = f"RSI extremo {rsi} mas margem limitada ({margem_percent:.1f}%)"
        
        logger.info(f"🎯 OVERSOLD_EXTREMO: RSI={rsi}, urgência={urgencia}")
        
        return {
            "decisao": "COMPRAR",
            "setup_4h": "OVERSOLD_EXTREMO",
            "urgencia": urgencia,
            "justificativa": justificativa
        }
        
    except Exception as e:
        logger.error(f"❌ Erro oversold extremo: {str(e)}")
        return _estrategia_erro(f"Erro oversold: {str(e)}")

def _processar_pullback_tendencia(setup_info: Dict, dados_alavancagem: Dict) -> Dict[str, Any]:
    """Processa setup PULLBACK_TENDENCIA (RSI < 45 + EMA144 ±3%)"""
    try:
        rsi = setup_info['condicoes']['rsi'] 
        ema_distance = setup_info['condicoes']['ema_distance']
        tamanho = setup_info['tamanho_posicao']
        
        # Determinar urgência baseada na qualidade do setup
        if rsi < 35 and abs(ema_distance) < 2:
            urgencia = "alta"
            qualidade = "excelente"
        elif rsi < 40:
            urgencia = "media"
            qualidade = "boa"
        else:
            urgencia = "baixa" 
            qualidade = "regular"
        
        justificativa = f"Pullback {qualidade}: RSI {rsi} + EMA dist {ema_distance:+.1f}% - posição {tamanho}%"
        
        logger.info(f"🎯 PULLBACK_TENDENCIA: RSI={rsi}, EMA={ema_distance:+.1f}%, urgência={urgencia}")
        
        return {
            "decisao": "COMPRAR",
            "setup_4h": "PULLBACK_TENDENCIA", 
            "urgencia": urgencia,
            "justificativa": justificativa
        }
        
    except Exception as e:
        logger.error(f"❌ Erro pullback tendência: {str(e)}")
        return _estrategia_erro(f"Erro pullback: {str(e)}")

def _processar_teste_suporte(setup_info: Dict, dados_alavancagem: Dict) -> Dict[str, Any]:
    """Processa setup TESTE_SUPORTE (toca EMA144)"""
    try:
        ema_distance = setup_info['condicoes']['ema_distance']
        tamanho = setup_info['tamanho_posicao']
        
        # Urgência baseada na proximidade da EMA144
        if abs(ema_distance) < 1:
            urgencia = "media"
            precisao = "preciso"
        else:
            urgencia = "baixa"
            precisao = "próximo"
        
        justificativa = f"Teste suporte {precisao}: EMA144 dist {ema_distance:+.1f}% - posição {tamanho}%"
        
        logger.info(f"🎯 TESTE_SUPORTE: EMA_dist={ema_distance:+.1f}%, urgência={urgencia}")
        
        return {
            "decisao": "COMPRAR",
            "setup_4h": "TESTE_SUPORTE",
            "urgencia": urgencia,
            "justificativa": justificativa
        }
        
    except Exception as e:
        logger.error(f"❌ Erro teste suporte: {str(e)}")
        return _estrategia_erro(f"Erro teste suporte: {str(e)}")

def _processar_rompimento(setup_info: Dict, dados_alavancagem: Dict) -> Dict[str, Any]:
    """Processa setup ROMPIMENTO (acima resistência)"""
    try:
        ema_distance = setup_info['condicoes']['ema_distance']
        rsi = setup_info['condicoes']['rsi']
        tamanho = setup_info['tamanho_posicao']
        
        # Urgência baseada na força do rompimento
        if ema_distance > 8 and rsi < 60:
            urgencia = "alta"
            forca = "forte"
        elif ema_distance > 6:
            urgencia = "media"
            forca = "moderado"
        else:
            urgencia = "baixa"
            forca = "fraco"
        
        justificativa = f"Rompimento {forca}: +{ema_distance:.1f}% EMA144, RSI {rsi} - posição {tamanho}%"
        
        logger.info(f"🎯 ROMPIMENTO: EMA_dist=+{ema_distance:.1f}%, RSI={rsi}, urgência={urgencia}")
        
        return {
            "decisao": "COMPRAR",
            "setup_4h": "ROMPIMENTO",
            "urgencia": urgencia,
            "justificativa": justificativa
        }
        
    except Exception as e:
        logger.error(f"❌ Erro rompimento: {str(e)}")
        return _estrategia_erro(f"Erro rompimento: {str(e)}")

def _estrategia_aguardar(motivo: str) -> Dict[str, Any]:
    """Estratégia aguardar quando não há setup válido"""
    return {
        "decisao": "AGUARDAR",
        "setup_4h": "NENHUM",
        "urgencia": "baixa",
        "justificativa": motivo
    }

def _estrategia_erro(erro: str) -> Dict[str, Any]:
    """Estratégia erro em caso de falha"""
    return {
        "decisao": "ERRO",
        "setup_4h": "INDISPONIVEL",
        "urgencia": "alta",
        "justificativa": erro
    }