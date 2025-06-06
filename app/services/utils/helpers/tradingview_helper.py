# app/services/utils/helpers/tradingview_helper.py - UNIFICADO E MODERNIZADO

import logging
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
from app.config import get_settings
from typing import Optional, Dict, Union

logger = logging.getLogger(__name__)

class TradingViewSession:
    """
    Singleton para gerenciar conexão TradingView
    MODERNIZADO: Remove auto_login deprecated e adiciona fallback robusto
    """
    _instance = None
    _connection_tested = False

    @classmethod
    def get_session(cls, force_reconnect: bool = False) -> TvDatafeed:
        """
        Obtém sessão TradingView com fallback robusto
        
        Args:
            force_reconnect: Força nova conexão mesmo se já existe
            
        Returns:
            TvDatafeed: Instância conectada
            
        Raises:
            Exception: Se não conseguir conectar
        """
        if cls._instance is None or force_reconnect:
            cls._instance = cls._create_connection()
            cls._connection_tested = False
        
        # Testar conexão na primeira vez
        if not cls._connection_tested:
            cls._test_connection()
            cls._connection_tested = True
            
        return cls._instance

    @classmethod
    def _create_connection(cls) -> TvDatafeed:
        """Cria conexão TradingView com fallback"""
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

    @classmethod
    def _test_connection(cls) -> bool:
        """Testa se a conexão está funcionando"""
        try:
            # Teste simples: buscar 1 barra de dados
            test_df = cls._instance.get_hist(
                symbol='BTCUSDT',
                exchange='BINANCE',
                interval=Interval.in_daily,
                n_bars=1
            )
            
            if test_df is not None and not test_df.empty:
                logger.info("✅ Conexão TradingView testada com sucesso")
                return True
            else:
                raise Exception("Teste retornou dados vazios")
                
        except Exception as e:
            logger.error(f"❌ Teste de conexão TradingView falhou: {str(e)}")
            raise Exception(f"Conexão TradingView não funcional: {str(e)}")

def get_tv_datafeed(force_reconnect: bool = False) -> TvDatafeed:
    """
    Função pública para obter sessão TradingView
    COMPATIBILIDADE: Mantém interface original
    """
    return TradingViewSession.get_session(force_reconnect)

def fetch_ohlc_data(
    symbol: str = "BTCUSDT",
    exchange: str = "BINANCE", 
    interval: Interval = Interval.in_daily,
    n_bars: int = 100,
    validate_data: bool = True
) -> pd.DataFrame:
    """
    NOVA FUNÇÃO: Busca dados OHLC padronizada e reutilizável
    
    Args:
        symbol: Símbolo (ex: BTCUSDT)
        exchange: Exchange (ex: BINANCE)
        interval: Timeframe (Interval.in_daily, in_weekly, etc)
        n_bars: Número de barras
        validate_data: Se deve validar os dados
        
    Returns:
        pd.DataFrame: Dados OHLC
        
    Raises:
        Exception: Se dados indisponíveis ou inválidos
    """
    try:
        logger.info(f"📊 Buscando {symbol} {exchange} {interval} ({n_bars} barras)")
        
        tv = get_tv_datafeed()
        
        df = tv.get_hist(
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            n_bars=n_bars
        )
        
        if df is None or df.empty:
            raise Exception(f"TradingView retornou dados vazios para {symbol}")
        
        if validate_data:
            _validate_ohlc_data(df, symbol, n_bars)
        
        logger.info(f"✅ {len(df)} barras obtidas - período: {df.index[0]} a {df.index[-1]}")
        return df
        
    except Exception as e:
        logger.error(f"❌ Erro buscando dados {symbol}: {str(e)}")
        raise Exception(f"Dados {symbol} indisponíveis: {str(e)}")

def _validate_ohlc_data(df: pd.DataFrame, symbol: str, expected_bars: int) -> None:
    """Valida dados OHLC"""
    if len(df) < expected_bars * 0.8:  # Tolerância de 20%
        raise Exception(f"Dados insuficientes: {len(df)} < {expected_bars * 0.8}")
    
    # Verificar colunas obrigatórias
    required_cols = ['open', 'high', 'low', 'close']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise Exception(f"Colunas faltantes: {missing_cols}")
    
    # Verificar valores válidos
    if df['close'].isna().any():
        raise Exception("Dados contêm valores NaN")
    
    # Validar range de preços para BTC
    if symbol.startswith('BTC'):
        close_prices = df['close']
        if not (1000 <= close_prices.min() <= 500000 and 1000 <= close_prices.max() <= 500000):
            logger.warning(f"⚠️ Preços BTC fora do range esperado: min={close_prices.min()}, max={close_prices.max()}")

def calculate_ema(prices: pd.Series, period: int) -> pd.Series:
    """
    NOVA FUNÇÃO: Calcula EMA padronizada
    
    Args:
        prices: Série de preços
        period: Período da EMA
        
    Returns:
        pd.Series: EMA calculada
    """
    try:
        if len(prices) < period:
            raise Exception(f"Dados insuficientes: {len(prices)} < {period}")
        
        ema = prices.ewm(span=period, adjust=False).mean()
        
        if ema.isna().any():
            raise Exception("EMA contém valores NaN")
        
        return ema
        
    except Exception as e:
        logger.error(f"❌ Erro calculando EMA{period}: {str(e)}")
        raise Exception(f"EMA{period} falhou: {str(e)}")

def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    NOVA FUNÇÃO: Calcula RSI padronizado
    
    Args:
        prices: Série de preços de fechamento
        period: Período do RSI (padrão 14)
        
    Returns:
        pd.Series: RSI calculado (0-100)
    """
    try:
        if len(prices) < period:
            raise Exception(f"Dados insuficientes: {len(prices)} < {period}")
        
        # Calcular mudanças
        delta = prices.diff()
        
        # Separar ganhos e perdas
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calcular médias móveis
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        # Calcular RS e RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        if rsi.isna().any():
            raise Exception("RSI contém valores NaN")
        
        return rsi
        
    except Exception as e:
        logger.error(f"❌ Erro calculando RSI: {str(e)}")
        raise Exception(f"RSI falhou: {str(e)}")

def get_ema144_distance(symbol: str = "BTCUSDT", exchange: str = "BINANCE") -> float:
    """
    NOVA FUNÇÃO: EMA144 distance reutilizável
    Substitui a função específica do ema144_live_helper
    """
    try:
        logger.info(f"📊 Calculando EMA144 distance para {symbol}...")
        
        # Buscar dados via função padronizada
        df = fetch_ohlc_data(
            symbol=symbol,
            exchange=exchange,
            interval=Interval.in_daily,
            n_bars=200  # Suficiente para EMA144
        )
        
        # Calcular EMA144 via função padronizada
        ema_144 = calculate_ema(df['close'], period=144)
        
        # Preço atual e EMA144 atual
        preco_atual = float(df['close'].iloc[-1])
        ema_144_atual = float(ema_144.iloc[-1])
        
        # Calcular distância percentual
        distance_percent = ((preco_atual - ema_144_atual) / ema_144_atual) * 100
        
        logger.info(f"✅ EMA144: ${ema_144_atual:,.2f}, Preço: ${preco_atual:,.2f}, Distância: {distance_percent:+.2f}%")
        
        return round(distance_percent, 2)
        
    except Exception as e:
        logger.error(f"❌ Erro EMA144 distance: {str(e)}")
        raise Exception(f"EMA144 distance indisponível: {str(e)}")

def get_rsi_current(
    symbol: str = "BTCUSDT", 
    exchange: str = "BINANCE",
    timeframe: Interval = Interval.in_daily,
    period: int = 14
) -> float:
    """
    NOVA FUNÇÃO: RSI atual reutilizável
    Substitui funções específicas do rsi_helper
    """
    try:
        logger.info(f"📊 Calculando RSI{period} {timeframe} para {symbol}...")
        
        # Buscar dados via função padronizada
        df = fetch_ohlc_data(
            symbol=symbol,
            exchange=exchange,
            interval=timeframe,
            n_bars=50  # Suficiente para RSI14
        )
        
        # Calcular RSI via função padronizada
        rsi = calculate_rsi(df['close'], period=period)
        
        # RSI atual
        rsi_atual = float(rsi.iloc[-1])
        
        # Validar range
        if not (0 <= rsi_atual <= 100):
            raise Exception(f"RSI inválido: {rsi_atual}")
        
        tf_display = "Diário" if timeframe == Interval.in_daily else "Mensal" if timeframe == Interval.in_monthly else str(timeframe)
        logger.info(f"✅ RSI{period} {tf_display}: {rsi_atual:.1f}")
        
        return round(rsi_atual, 1)
        
    except Exception as e:
        logger.error(f"❌ Erro RSI: {str(e)}")
        raise Exception(f"RSI indisponível: {str(e)}")

def calculate_bollinger_bands(
    prices: pd.Series,
    period: int = 20,
    std_dev: float = 2.0
) -> Dict[str, pd.Series]:
    """
    NOVA FUNÇÃO: Bollinger Bands padronizadas
    
    Returns:
        Dict com 'upper', 'lower', 'middle'
    """
    try:
        if len(prices) < period:
            raise Exception(f"Dados insuficientes: {len(prices)} < {period}")
        
        # Middle Band (SMA)
        middle = prices.rolling(window=period).mean()
        
        # Standard Deviation
        std = prices.rolling(window=period).std()
        
        # Upper e Lower Bands
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return {
            'upper': upper,
            'middle': middle,
            'lower': lower
        }
        
    except Exception as e:
        logger.error(f"❌ Erro Bollinger Bands: {str(e)}")
        raise Exception(f"Bollinger Bands falhou: {str(e)}")

# COMPATIBILIDADE: Manter funções antigas para não quebrar imports existentes
def get_tv_session():
    """DEPRECATED: Use get_tv_datafeed()"""
    return get_tv_datafeed()

# HEALTH CHECK
def test_tradingview_connection() -> Dict:
    """Testa conexão TradingView e retorna status"""
    try:
        tv = get_tv_datafeed(force_reconnect=True)
        
        # Teste básico
        df = tv.get_hist('BTCUSDT', 'BINANCE', Interval.in_daily, 1)
        
        if df is not None and not df.empty:
            return {
                "status": "success",
                "message": "TradingView conectado e funcional",
                "test_data": f"Última barra: {df.index[-1]}",
                "connection_type": "com_login" if hasattr(get_settings(), 'TV_USERNAME') and get_settings().TV_USERNAME else "anonimo"
            }
        else:
            return {
                "status": "error",
                "message": "TradingView conectado mas retornou dados vazios"
            }
            
    except Exception as e:
        return {
            "status": "error", 
            "message": f"TradingView falhou: {str(e)}"
        }