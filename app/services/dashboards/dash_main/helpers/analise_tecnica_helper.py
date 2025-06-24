# app/services/dashboards/dash_main/helpers/analise_tecnica_helper.py

import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

def get_todos_dados_tecnicos() -> Dict[str, Any]:
    """
    Busca TODOS dados técnicos necessários para setups
    
    Returns:
        Dict com todos dados técnicos consolidados
    """
    try:
        logger.info("📊 Coletando dados técnicos consolidados...")
        
        # IMPLEMENTANDO: RSI 4H real via TradingView
        rsi_4h = _buscar_rsi_4h()
        logger.info(f"📊 RSI 4H real: {rsi_4h}")
        
        # IMPLEMENTANDO: EMAs para cruzamento real via TradingView  
        emas_data = _buscar_emas_17_34_4h()
        
        dados_consolidados = {
            "rsi_4h": rsi_4h,
            "precos": {
                "atual": emas_data.get('preco_atual', 103500.0),
                "ema_17": emas_data.get('ema_17_atual', 103200.0),
                "ema_144": 103000.0  # TODO: buscar real
            },
            "distancias": {
                "ema_144_distance": 0.48,  # TODO: calcular real
                "ema_17_distance": 0.29    # TODO: calcular real
            },
            "emas_cruzamento": {
                "ema_17_atual": emas_data.get('ema_17_atual'),
                "ema_34_atual": emas_data.get('ema_34_atual'),
                "ema_17_anterior": emas_data.get('ema_17_anterior'),
                "ema_34_anterior": emas_data.get('ema_34_anterior')
            },
            "timestamp": datetime.utcnow().isoformat(),
            "source": "tradingview_rsi4h_emas_real"
        }
        
        logger.info(f"📊 RSI 4H: {rsi_4h}, Status: Real TradingView")
        
        return dados_consolidados
        
    except Exception as e:
        logger.error(f"❌ Erro obter dados técnicos: {str(e)}")
        raise Exception(f"Falha buscar dados técnicos: {str(e)}")

def _buscar_rsi_4h() -> float:
    """Busca RSI 4H via TradingView"""
    try:
        from app.services.utils.helpers.tradingview.tradingview_helper import get_rsi_current
        from tvDatafeed import Interval
        
        rsi = get_rsi_current(
            symbol="BTCUSDT",
            exchange="BINANCE", 
            timeframe=Interval.in_4_hour,
            period=14
        )
        
        if not (0 <= rsi <= 100):
            raise ValueError(f"RSI 4H inválido: {rsi}")
            
        return round(rsi, 1)
        
    except Exception as e:
        logger.error(f"❌ Erro RSI 4H: {str(e)}")
        raise Exception(f"RSI 4H indisponível: {str(e)}")

def _buscar_emas_17_34_4h() -> Dict[str, float]:
    """Busca EMAs 17 e 34 timeframe 4H via TradingView"""
    try:
        from app.services.utils.helpers.tradingview.tradingview_helper import fetch_ohlc_data, calculate_ema
        from tvDatafeed import Interval
        
        # Buscar dados 4H com barras suficientes para EMA34
        df = fetch_ohlc_data(
            symbol="BTCUSDT",
            exchange="BINANCE", 
            interval=Interval.in_4_hour,
            n_bars=100  # Suficiente para EMA34 + buffer
        )
        
        # Calcular EMAs
        ema_17 = calculate_ema(df['close'], period=17)
        ema_34 = calculate_ema(df['close'], period=34)
        
        # Valores atuais (última barra)
        ema_17_atual = float(ema_17.iloc[-1])
        ema_34_atual = float(ema_34.iloc[-1])
        preco_atual = float(df['close'].iloc[-1])
        
        # Valores anteriores (penúltima barra) para detectar cruzamento
        ema_17_anterior = float(ema_17.iloc[-2])
        ema_34_anterior = float(ema_34.iloc[-2])
        
        # Validações
        if any(v <= 0 for v in [ema_17_atual, ema_34_atual, ema_17_anterior, ema_34_anterior]):
            raise ValueError("EMAs com valores inválidos")
        
        return {
            "ema_17_atual": ema_17_atual,
            "ema_34_atual": ema_34_atual,
            "ema_17_anterior": ema_17_anterior,
            "ema_34_anterior": ema_34_anterior,
            "preco_atual": preco_atual
        }
        
    except Exception as e:
        logger.error(f"❌ Erro EMAs 4H: {str(e)}")
        raise Exception(f"EMAs 4H indisponíveis: {str(e)}")

def _calcular_distancias(preco_atual: float, ema_17: float, ema_144: float) -> Dict[str, float]:
    """Calcula distâncias percentuais das EMAs"""
    return {
        "ema_144_distance": ((preco_atual - ema_144) / ema_144) * 100,
        "ema_17_distance": ((preco_atual - ema_17) / ema_17) * 100
    }