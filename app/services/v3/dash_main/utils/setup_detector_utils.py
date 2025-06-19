# app/services/v3/dash_main/utils/setup_detector_utils.py

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def identificar_setup_4h(tecnicos: Dict, gate_result: Dict) -> Dict[str, Any]:
    """
    Identifica setup 4H baseado na Matriz de Setups
    
    Setups de COMPRA:
    - Pullback Tendência: RSI < 45 + EMA144 ±3%
    - Teste Suporte: Toca EMA144 + Bounce  
    - Rompimento: Fecha acima resistência
    - Oversold Extremo: RSI < 30
    
    Args:
        tecnicos: Dict com RSI, EMA distance, preço
        gate_result: Resultado do gate system
    
    Returns:
        Dict com setup identificado, força e detalhes
    """
    try:
        logger.info("🔍 Identificando setup 4H...")
        
        # Se gate bloqueou, não identificar setup
        if not gate_result.get('liberado', False):
            logger.info("🚫 Gate bloqueado - não identificar setup")
            return _setup_nenhum("Gate system bloqueado")
        
        # EXTRAIR DADOS TÉCNICOS
        rsi = tecnicos.get('rsi', 50)
        ema_distance = tecnicos.get('ema_144_distance', 0)
        
        logger.info(f"📊 Análise Setup: RSI={rsi}, EMA_dist={ema_distance}%")
        
        # IDENTIFICAR SETUPS EM ORDEM DE PRIORIDADE
        
        # 1. OVERSOLD EXTREMO (maior prioridade)
        if rsi < 30:
            logger.info(f"🎯 Setup OVERSOLD_EXTREMO identificado: RSI={rsi} < 30")
            return {
                "setup": "OVERSOLD_EXTREMO",
                "forca": "muito_alta",
                "tamanho_posicao": 40,
                "condicoes": {
                    "rsi": rsi,
                    "limite_rsi": 30,
                    "confirmacao": "RSI extremamente oversold"
                },
                "detalhes": f"RSI extremo {rsi} indica forte oportunidade de compra"
            }
        
        # 2. PULLBACK TENDÊNCIA 
        if rsi < 45 and -3 <= ema_distance <= 3:
            logger.info(f"🎯 Setup PULLBACK_TENDENCIA identificado: RSI={rsi} < 45, EMA_dist={ema_distance}% ±3%")
            return {
                "setup": "PULLBACK_TENDENCIA",
                "forca": "alta",
                "tamanho_posicao": 30,
                "condicoes": {
                    "rsi": rsi,
                    "limite_rsi": 45,
                    "ema_distance": ema_distance,
                    "ema_range": "±3%",
                    "confirmacao": "RSI oversold próximo EMA144"
                },
                "detalhes": f"Pullback na tendência: RSI {rsi} + EMA dist {ema_distance}%"
            }
        
        # 3. TESTE SUPORTE (toca EMA144)
        if -2 <= ema_distance <= 2:
            logger.info(f"🎯 Setup TESTE_SUPORTE identificado: EMA_dist={ema_distance}% ±2%")
            return {
                "setup": "TESTE_SUPORTE", 
                "forca": "media",
                "tamanho_posicao": 25,
                "condicoes": {
                    "ema_distance": ema_distance,
                    "ema_range": "±2%",
                    "confirmacao": "Preço tocando EMA144"
                },
                "detalhes": f"Teste suporte EMA144: distância {ema_distance}%"
            }
        
        # 4. ROMPIMENTO (acima resistência - estimativa por EMA distance)
        if ema_distance > 5 and rsi < 70:
            logger.info(f"🎯 Setup ROMPIMENTO identificado: EMA_dist={ema_distance}% > 5%, RSI={rsi} < 70")
            return {
                "setup": "ROMPIMENTO",
                "forca": "media", 
                "tamanho_posicao": 20,
                "condicoes": {
                    "ema_distance": ema_distance,
                    "limite_ema": 5,
                    "rsi": rsi,
                    "limite_rsi": 70,
                    "confirmacao": "Preço acima EMA144 sem overbought"
                },
                "detalhes": f"Rompimento: {ema_distance}% acima EMA144, RSI {rsi}"
            }
        
        # NENHUM SETUP IDENTIFICADO
        logger.info("❌ Nenhum setup identificado")
        return _setup_nenhum(f"RSI={rsi}, EMA_dist={ema_distance}% - condições não atendidas")
        
    except Exception as e:
        logger.error(f"❌ Erro identificação setup: {str(e)}")
        return _setup_nenhum(f"Erro: {str(e)}")

def _setup_nenhum(motivo: str) -> Dict[str, Any]:
    """Retorna setup 'NENHUM' com motivo"""
    return {
        "setup": "NENHUM",
        "forca": "nenhuma",
        "tamanho_posicao": 0,
        "condicoes": {},
        "detalhes": motivo
    }

def validar_setup_confirmacao(setup_info: Dict, dados_volume: Dict = None) -> Dict[str, Any]:
    """
    FUNÇÃO FUTURA: Validar confirmação do setup com volume/candlestick
    
    TODO: Implementar quando dados de volume estiverem disponíveis
    - Volume médio+ para Pullback
    - Martelo/Doji para Teste Suporte  
    - Volume alto para Rompimento
    - Divergência+ para Oversold Extremo
    """
    logger.info("🔄 Validação confirmação setup - TODO: implementar volume/candlestick")
    
    # Por enquanto, retorna setup sem modificação
    setup_info["confirmacao_disponivel"] = False
    setup_info["confirmacao_motivo"] = "Dados volume/candlestick não implementados"
    
    return setup_info