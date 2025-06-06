# app/services/utils/helpers/analise/ema144_live_helper.py - SIMPLIFICADO

import logging
from app.services.utils.helpers.tradingview_helper import get_ema144_distance, fetch_ohlc_data
from tvDatafeed import Interval

logger = logging.getLogger(__name__)

def obter_ema144_distance_atualizada():
    """
    SIMPLIFICADO: Usa TradingView helper unificado
    Mantém interface original para compatibilidade
    """
    try:
        logger.info("📊 Buscando EMA144 distance via TradingView helper...")
        
        # Usar função unificada do TradingView helper
        distance_percent = get_ema144_distance()
        
        logger.info(f"✅ EMA144 distance obtida: {distance_percent:+.2f}%")
        return distance_percent
            
    except Exception as e:
        logger.error(f"❌ Erro obtendo EMA144 distance: {str(e)}")
        raise Exception(f"EMA144 distance indisponível: {str(e)}")

def obter_dados_completos_ema144_distance_atualizada():
    """
    SIMPLIFICADO: Usa TradingView helper para dados completos
    """
    try:
        logger.info("📊 Buscando dados completos EMA144...")
        
        # Buscar dados via helper unificado
        df = fetch_ohlc_data(
            symbol="BTCUSDT",
            exchange="BINANCE",
            interval=Interval.in_daily,
            n_bars=200
        )
        
        # Calcular EMA144 via helper unificado
        from app.services.utils.helpers.tradingview_helper import calculate_ema
        ema_144 = calculate_ema(df['close'], period=144)
        
        # Valores atuais
        preco_atual = float(df['close'].iloc[-1])
        ema_144_valor = float(ema_144.iloc[-1])
        distance_percent = ((preco_atual - ema_144_valor) / ema_144_valor) * 100
        
        logger.info(f"✅ Dados completos EMA144 obtidos")

        return {
            "distance_percent": round(distance_percent, 2),
            "preco_atual": preco_atual,
            "ema_144_daily": ema_144_valor,
            "timeframe": "1D",
            "fonte": "tradingview_helper_unificado",
            "barras_utilizadas": len(df)
        }
        
    except Exception as e:
        logger.error(f"❌ Erro dados completos EMA144: {str(e)}")
        raise Exception(f"Dados completos EMA144 indisponíveis: {str(e)}")

# WRAPPER para compatibilidade
def obter_ema144_distance():
    """Wrapper para compatibilidade com código existente"""
    return obter_ema144_distance_atualizada()

# FUNÇÃO DEBUG simplificada
def debug_ema144_calculation():
    """DEBUG simplificado usando TradingView helper"""
    try:
        logger.info("🔍 DEBUG EMA144 via TradingView helper:")
        
        # Usar helper unificado para buscar dados
        df = fetch_ohlc_data("BTCUSDT", "BINANCE", Interval.in_daily, 200)
        
        # Calcular múltiplas EMAs para comparação
        from app.services.utils.helpers.tradingview_helper import calculate_ema
        
        ema_17 = calculate_ema(df['close'], 17).iloc[-1]
        ema_34 = calculate_ema(df['close'], 34).iloc[-1]
        ema_144 = calculate_ema(df['close'], 144).iloc[-1]
        
        logger.info(f"📊 DataFrame shape: {df.shape}")
        logger.info(f"📊 EMA17: {ema_17:.2f}")
        logger.info(f"📊 EMA34: {ema_34:.2f}")
        logger.info(f"📊 EMA144: {ema_144:.2f}")
        
        # Verificar ordem bullish
        if ema_17 > ema_34 > ema_144:
            logger.info("✅ EMAs em ordem bullish")
        else:
            logger.warning("⚠️ EMAs não estão em ordem bullish")
            
        return True
            
    except Exception as e:
        logger.error(f"❌ Erro no debug: {str(e)}")
        return False