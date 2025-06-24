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
        
        # TODO: EMAs e preços reais (próximos setups)
        dados_consolidados = {
            "rsi_4h": rsi_4h,
            "precos": {
                "atual": 103500.0,  # TODO: buscar real
                "ema_17": 103200.0,  # TODO: buscar real
                "ema_144": 103000.0  # TODO: buscar real
            },
            "distancias": {
                "ema_144_distance": 0.48,  # TODO: calcular real
                "ema_17_distance": 0.29    # TODO: calcular real
            },
            "timestamp": datetime.utcnow().isoformat(),
            "source": "tradingview_rsi4h_real"
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

def _buscar_precos_emas() -> Dict[str, float]:
    """Busca preços e EMAs via TradingView (implementar depois)"""
    # TODO: Implementar tradingview_helper.calculate_ema()
    pass

def _calcular_distancias(preco_atual: float, ema_17: float, ema_144: float) -> Dict[str, float]:
    """Calcula distâncias percentuais das EMAs"""
    return {
        "ema_144_distance": ((preco_atual - ema_144) / ema_144) * 100,
        "ema_17_distance": ((preco_atual - ema_17) / ema_17) * 100
    }