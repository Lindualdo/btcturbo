# app/services/utils/helpers/dashboard_home/estrategia/estrategia_formatacao_helper.py

import logging
from app.services.utils.helpers.tradingview.tradingview_helper import fetch_ohlc_data, calculate_ema, get_tv_datafeed
from tvDatafeed import Interval

logger = logging.getLogger(__name__)

def obter_dados_btc_validados() -> tuple[float, float, str]:
    """
    Obter dados BTC com força reconexão e validação rigorosa
    
    Returns:
        tuple: (ema_valor, btc_price, timestamp)
    """
    try:
        logger.info("🔄 Forçando reconexão TradingView para dados atualizados...")
        
        # Força nova conexão
        tv = get_tv_datafeed(force_reconnect=True)
        
        # Buscar dados recentes (100 períodos para EMA144)
        data = fetch_ohlc_data(
            symbol="BTCUSDT",
            exchange="BINANCE",
            interval=Interval.in_daily,
            n_bars=2000  # Margem para EMA144
        )
        
        if data is None or len(data) < 144:
            raise Exception("Dados BTC insuficientes para EMA144")
        
        # Calcular EMA144 atual
        ema_values = calculate_ema(data['close'], period=144)
        
        # Dados mais recentes
        btc_price = float(data['close'].iloc[-1])
        ema_valor = float(ema_values.iloc[-1])
        data_timestamp = data.index[-1].strftime('%Y-%m-%d %H:%M:%S')
        
        logger.info(f"✅ Dados BTC validados: ${btc_price:,.2f} | EMA144: ${ema_valor:,.2f}")
        
        return ema_valor, btc_price, data_timestamp
        
    except Exception as e:
        logger.error(f"❌ Erro obtendo dados BTC: {str(e)}")
        raise

def mapear_decisao_cenario(decisao_cenario: str) -> str:
    """
    Mapeia decisões de cenários para ações padrão
    
    Args:
        decisao_cenario: Decisão do cenário específico
    
    Returns:
        str: Ação padrão mapeada
    """
    mapeamento = {
        "ENTRAR": "ADICIONAR",
        "ADICIONAR_AGRESSIVO": "ADICIONAR", 
        "REALIZAR_PARCIAL": "REALIZAR",
        "REALIZAR_AGRESSIVO": "REALIZAR",
        "REDUZIR_DEFENSIVO": "REALIZAR",
        "EMERGENCIA_REDUZIR": "REALIZAR",
        "ACUMULAR_SPOT_APENAS": "ADICIONAR",
        "MATRIZ_TATICA_BASICA": "HOLD"
    }
    return mapeamento.get(decisao_cenario, "HOLD")

def determinar_urgencia(cenario: dict) -> str:
    """
    Determina urgência baseada no cenário
    
    Args:
        cenario: Dicionário do cenário identificado
    
    Returns:
        str: Nível de urgência (critica, alta, media, baixa)
    """
    if cenario.get("override"):
        return "critica"
    elif cenario["prioridade"] <= 1:
        return "alta"
    elif cenario["prioridade"] <= 2:
        return "media"
    else:
        return "baixa"