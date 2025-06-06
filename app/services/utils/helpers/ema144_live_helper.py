# app/services/utils/helpers/ema144_live_helper.py

import logging
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
from app.config import get_settings

logger = logging.getLogger(__name__)

def obter_ema144_distance_atualizada():
    """
    Busca EMA144 e preço atual via TradingView (dados atualizados)
    Baseado em ema_calculator.py
    """
    try:
        logger.info("📊 Buscando EMA144 atualizada via TradingView...")
        
        # 1. Conectar TradingView (baseado em ema_calculator.py)
        tv = _get_tv_session()
        
        # 2. Buscar dados semanal (EMA144 é calculada em timeframe semanal)
        df = tv.get_hist(
            symbol="BTCUSDT",
            exchange="BINANCE",
            interval=Interval.in_weekly,
            n_bars=700  # Suficiente para EMA 610 (maior período)
        )
        
        if df is None or df.empty:
            raise Exception("Dados TradingView indisponíveis")
        
        if len(df) < 144:
            raise Exception(f"Dados insuficientes: {len(df)} barras < 144 necessárias")
        
        # 3. Calcular EMA144
        ema_144_series = df['close'].ewm(span=144, adjust=False).mean()
        ema_144_valor = float(ema_144_series.iloc[-1])
        
        # 4. Preço atual (última barra)
        preco_atual = float(df['close'].iloc[-1])
        
        # 5. Calcular distância percentual
        distance_percent = ((preco_atual - ema_144_valor) / ema_144_valor) * 100
        
        logger.info(f"✅ EMA144 atualizada: ${ema_144_valor:,.2f}")
        logger.info(f"✅ Preço atual: ${preco_atual:,.2f}")
        logger.info(f"✅ Distância: {distance_percent:+.2f}%")
        
        return {
            "distance_percent": round(distance_percent, 2),
            "preco_atual": preco_atual,
            "ema_144": ema_144_valor,
            "timeframe": "1W",
            "fonte": "tradingview_live",
            "barras_utilizadas": len(df)
        }
        
    except Exception as e:
        logger.error(f"❌ Erro obtendo EMA144 atualizada: {str(e)}")
        raise Exception(f"EMA144 distance atualizada indisponível: {str(e)}")

def _get_tv_session():
    """
    Conecta TradingView (baseado em ema_calculator.py)
    """
    try:
        settings = get_settings()
        
        # Tentar com credenciais primeiro
        if hasattr(settings, 'TV_USERNAME') and settings.TV_USERNAME and settings.TV_PASSWORD:
            try:
                logger.info("🔗 Conectando TradingView com credenciais...")
                tv = TvDatafeed(
                    username=settings.TV_USERNAME,
                    password=settings.TV_PASSWORD
                )
                logger.info("✅ TradingView conectado com login")
                return tv
            except Exception as e:
                logger.warning(f"⚠️ Login TradingView falhou: {e}")
        
        # Fallback: modo anônimo
        logger.info("🔗 Conectando TradingView modo anônimo...")
        tv = TvDatafeed()
        logger.info("✅ TradingView conectado sem login")
        return tv
        
    except Exception as e:
        logger.error(f"❌ Erro conectando TradingView: {str(e)}")
        raise Exception(f"Conexão TradingView falhou: {str(e)}")

def validar_ema144_data(ema_144: float, preco: float, distance: float) -> bool:
    """
    Valida se os dados EMA144 fazem sentido
    """
    try:
        # Validações básicas
        if ema_144 <= 0 or preco <= 0:
            logger.error(f"❌ Valores inválidos: EMA144={ema_144}, Preço={preco}")
            return False
        
        # EMA144 deve estar em range razoável do BTC
        if not (10000 <= ema_144 <= 200000):
            logger.error(f"❌ EMA144 fora do range: {ema_144}")
            return False
        
        # Preço deve estar em range razoável do BTC
        if not (10000 <= preco <= 200000):
            logger.error(f"❌ Preço fora do range: {preco}")
            return False
        
        # Distância não deve ser extrema (±100%)
        if abs(distance) > 100:
            logger.warning(f"⚠️ Distância extrema: {distance:.2f}%")
        
        logger.info("✅ Dados EMA144 validados")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na validação: {str(e)}")
        return False

def debug_ema144_calculation(df: pd.DataFrame):
    """
    DEBUG: Mostra detalhes do cálculo EMA144
    """
    try:
        logger.info("🔍 DEBUG EMA144:")
        logger.info(f"📊 DataFrame shape: {df.shape}")
        logger.info(f"📊 Últimos 5 closes: {df['close'].tail().tolist()}")
        
        # Calcular EMAs menores para comparação
        ema_17 = df['close'].ewm(span=17, adjust=False).mean().iloc[-1]
        ema_34 = df['close'].ewm(span=34, adjust=False).mean().iloc[-1]
        ema_144 = df['close'].ewm(span=144, adjust=False).mean().iloc[-1]
        
        logger.info(f"📊 EMA17: {ema_17:.2f}")
        logger.info(f"📊 EMA34: {ema_34:.2f}")
        logger.info(f"📊 EMA144: {ema_144:.2f}")
        
        # Verificar ordem das EMAs (deve ser crescente em bull market)
        if ema_17 > ema_34 > ema_144:
            logger.info("✅ EMAs em ordem bullish")
        else:
            logger.warning("⚠️ EMAs não estão em ordem bullish")
            
    except Exception as e:
        logger.error(f"❌ Erro no debug: {str(e)}")

# Função principal para uso no rsi_helper.py
def obter_ema144_distance():
    """
    Função principal: retorna apenas a distância percentual
    """
    try:
        resultado = obter_ema144_distance_atualizada()
        return resultado["distance_percent"]
    except Exception as e:
        raise Exception(f"EMA144 distance indisponível: {str(e)}")