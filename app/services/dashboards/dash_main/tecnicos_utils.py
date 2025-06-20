# source: app/services/dashboards/dash_main/tecnicos_utils.py

import logging
from typing import Dict
from app.services.utils.helpers.tradingview.tradingview_helper import (
    get_rsi_current, 
    fetch_ohlc_data, 
    calculate_ema
)
from tvDatafeed import Interval

logger = logging.getLogger(__name__)

def obter_dados_tecnicos_4h() -> Dict[str, float]:
    """
    Obtém dados técnicos 4H para análise de setup
    
    Returns:
        Dict com:
        - rsi: RSI 14 períodos 4H
        - preco_ema144: Valor da EMA144 4H  
        - ema_144_distance: Distância % do preço atual da EMA144
    """
    try:
        logger.info("📊 Coletando dados técnicos 4H...")
        
        # 1. RSI 4H usando helper existente
        rsi_4h = _obter_rsi_4h()
        logger.info(f"✅ RSI 4H: {rsi_4h}")
        
        # 2. EMA144 4H e cálculo de distância
        ema_data = _obter_ema144_4h_e_distancia()
        logger.info(f"✅ EMA144 4H: ${ema_data['preco_ema144']:,.2f}, Distância: {ema_data['ema_144_distance']:+.2f}%")
        
        return {
            "rsi": round(rsi_4h, 1),
            "preco_ema144": round(ema_data['preco_ema144'], 2),
            "ema_144_distance": round(ema_data['ema_144_distance'], 2)
        }
        
    except Exception as e:
        logger.error(f"❌ Erro dados técnicos 4H: {str(e)}")
        raise Exception(f"Dados técnicos 4H indisponíveis: {str(e)}")

def _obter_rsi_4h() -> float:
    """Obtém RSI 4H usando helper TradingView existente"""
    try:
        rsi_4h = get_rsi_current(
            symbol="BTCUSDT",
            exchange="BINANCE",
            timeframe=Interval.in_4_hour,
            period=14
        )
        
        # Validar range
        if not (0 <= rsi_4h <= 100):
            raise ValueError(f"RSI 4H fora do range: {rsi_4h}")
        
        return rsi_4h
        
    except Exception as e:
        logger.error(f"❌ Erro RSI 4H: {str(e)}")
        raise Exception(f"RSI 4H indisponível: {str(e)}")

def _obter_ema144_4h_e_distancia() -> Dict[str, float]:
    """Obtém EMA144 4H e calcula distância percentual"""
    try:
        # Buscar dados OHLC 4H
        df = fetch_ohlc_data(
            symbol="BTCUSDT",
            exchange="BINANCE", 
            interval=Interval.in_4_hour,
            n_bars=200  # Suficiente para EMA144
        )
        
        # Calcular EMA144
        ema_144 = calculate_ema(df['close'], period=144)
        
        # Valores atuais
        preco_atual = float(df['close'].iloc[-1])
        ema_144_atual = float(ema_144.iloc[-1])
        
        # Calcular distância percentual
        ema_distance = ((preco_atual - ema_144_atual) / ema_144_atual) * 100
        
        # Validar resultados
        if preco_atual <= 0 or ema_144_atual <= 0:
            raise ValueError(f"Preços inválidos: atual={preco_atual}, ema={ema_144_atual}")
        
        return {
            "preco_ema144": ema_144_atual,
            "ema_144_distance": ema_distance
        }
        
    except Exception as e:
        logger.error(f"❌ Erro EMA144 4H: {str(e)}")
        raise Exception(f"EMA144 4H indisponível: {str(e)}")

def obter_dados_tecnicos_complementares() -> Dict[str, float]:
    """
    FUNÇÃO FUTURA: Dados técnicos complementares para validação
    
    TODO: Implementar quando necessário:
    - MACD 4H
    - Volume médio
    - Bollinger Bands
    - ATR para stops
    """
    logger.info("🔄 Dados técnicos complementares - TODO: implementar quando necessário")
    
    return {
        "macd_implementar": False,
        "volume_implementar": False,
        "bollinger_implementar": False,
        "atr_implementar": False
    }