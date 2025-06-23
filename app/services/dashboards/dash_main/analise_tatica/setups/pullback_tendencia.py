import logging
from typing import Dict, Any
from app.services.utils.helpers.tradingview.tradingview_helper import get_rsi_current, fetch_ohlc_data, calculate_ema
from tvDatafeed import Interval

logger = logging.getLogger(__name__)

def detectar_pullback_tendencia() -> Dict[str, Any]:
    """
    Detecta setup PULLBACK TENDÊNCIA 4H
    
    Condições:
    - RSI 4H < 45
    - EMA144 4H distance ±3%
    
    Returns:
        Dict com resultado da detecção
    """
    try:
        logger.info("🔍 Detectando Pullback Tendência 4H...")
        
        # 1. BUSCAR RSI 4H
        rsi_4h = _obter_rsi_4h()
        logger.info(f"📊 RSI 4H: {rsi_4h}")
        
        # 2. BUSCAR EMA144 4H e distância
        ema_data = _obter_ema144_4h_e_distancia()
        ema_distance = ema_data['ema_144_distance']
        preco_ema144 = ema_data['preco_ema144']
        logger.info(f"📊 EMA144 4H: ${preco_ema144:,.2f}, Distância: {ema_distance:+.2f}%")
        
        # 3. VALIDAR CONDIÇÕES
        condicao_rsi = rsi_4h < 45
        condicao_ema = -3 <= ema_distance <= 3
        
        logger.info(f"🔍 RSI < 45: {condicao_rsi} ({rsi_4h})")
        logger.info(f"🔍 EMA ±3%: {condicao_ema} ({ema_distance:+.1f}%)")
        
        if condicao_rsi and condicao_ema:
            logger.info("✅ PULLBACK TENDÊNCIA identificado!")
            
            # Calcular força do setup
            forca = _calcular_forca_setup(rsi_4h, ema_distance)
            
            return {
                "encontrado": True,
                "setup": "PULLBACK_TENDENCIA",
                "forca": forca,
                "tamanho_posicao": 30,
                "dados_tecnicos": {
                    "rsi": rsi_4h,
                    "preco_ema144": preco_ema144,
                    "ema_144_distance": ema_distance
                },
                "condicoes": {
                    "rsi": rsi_4h,
                    "limite_rsi": 45,
                    "ema_distance": ema_distance,
                    "ema_range": "±3%"
                },
                "detalhes": f"Pullback tendência: RSI {rsi_4h} + EMA dist {ema_distance:+.1f}%"
            }
        else:
            logger.info("❌ Pullback Tendência não identificado")
            return {
                "encontrado": False,
                "setup": "PULLBACK_TENDENCIA",
                "dados_tecnicos": {
                    "rsi": rsi_4h,
                    "preco_ema144": preco_ema144,
                    "ema_144_distance": ema_distance
                },
                "detalhes": f"Condições não atendidas: RSI={rsi_4h} (<45: {condicao_rsi}), EMA={ema_distance:+.1f}% (±3%: {condicao_ema})"
            }
        
    except Exception as e:
        logger.error(f"❌ Erro Pullback Tendência: {str(e)}")
        return {
            "encontrado": False,
            "setup": "PULLBACK_TENDENCIA",
            "dados_tecnicos": {},
            "detalhes": f"Erro: {str(e)}"
        }

def _obter_rsi_4h() -> float:
    """Obtém RSI 4H usando helper TradingView"""
    try:
        rsi = get_rsi_current(
            symbol="BTCUSDT",
            exchange="BINANCE",
            timeframe=Interval.in_4_hour,
            period=14
        )
        
        if not (0 <= rsi <= 100):
            raise ValueError(f"RSI 4H fora do range: {rsi}")
        
        return round(rsi, 1)
        
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
            n_bars=200
        )
        
        # Calcular EMA144
        ema_144 = calculate_ema(df['close'], period=144)
        
        # Valores atuais
        preco_atual = float(df['close'].iloc[-1])
        ema_144_atual = float(ema_144.iloc[-1])
        
        # Calcular distância percentual
        ema_distance = ((preco_atual - ema_144_atual) / ema_144_atual) * 100
        
        if preco_atual <= 0 or ema_144_atual <= 0:
            raise ValueError(f"Preços inválidos: atual={preco_atual}, ema={ema_144_atual}")
        
        return {
            "preco_ema144": ema_144_atual,
            "ema_144_distance": ema_distance
        }
        
    except Exception as e:
        logger.error(f"❌ Erro EMA144 4H: {str(e)}")
        raise Exception(f"EMA144 4H indisponível: {str(e)}")

def _calcular_forca_setup(rsi: float, ema_distance: float) -> str:
    """Calcula força do setup baseado nas condições"""
    # Quanto menor RSI e mais próximo da EMA, mais forte
    if rsi < 35 and abs(ema_distance) < 1:
        return "muito_alta"
    elif rsi < 40 and abs(ema_distance) < 2:
        return "alta"
    elif rsi < 45 and abs(ema_distance) < 3:
        return "media"
    else:
        return "baixa"