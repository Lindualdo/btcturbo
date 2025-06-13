# app/services/utils/helpers/v2/dashboard_home/data_collector.py

import logging
from typing import Dict
from app.services.analises.analise_mercado import calcular_analise_mercado
from app.services.analises.analise_risco import calcular_analise_risco
from app.services.analises.analise_alavancagem import calcular_analise_alavancagem
from app.services.utils.helpers.tradingview.tradingview_helper import (
    get_ema144_distance, get_rsi_current, fetch_ohlc_data
)
from tvDatafeed import Interval

logger = logging.getLogger(__name__)

def collect_all_data() -> Dict:
    """
    Coleta TODOS os dados necessários em UMA operação
    Evita múltiplas consultas redundantes
    
    Returns:
        Dict com todos os dados consolidados
    """
    try:
        logger.info("📊 Coletando todos os dados (busca única)...")
        
        # 1. Análises principais (REUTILIZA funções existentes)
        mercado_data = _get_mercado_data()
        risco_data = _get_risco_data() 
        alavancagem_data = _get_alavancagem_data()
        
        # 2. Dados técnicos (REUTILIZA TradingView)
        technical_data = _get_technical_data()
        
        # 3. Consolidar tudo
        all_data = {
            **mercado_data,
            **risco_data,
            **alavancagem_data,
            **technical_data
        }
        
        logger.info("✅ Todos os dados coletados com sucesso")
        _log_data_summary(all_data)
        
        return all_data
        
    except Exception as e:
        logger.error(f"❌ Erro na coleta de dados: {str(e)}")
        raise Exception(f"Falha na coleta de dados: {str(e)}")

def _get_mercado_data() -> Dict:
    """Coleta dados de mercado"""
    try:
        mercado = calcular_analise_mercado()
        if mercado["status"] != "success":
            raise Exception(f"Análise mercado falhou: {mercado.get('erro')}")
        
        logger.info(f"🔍 Estrutura mercado: {list(mercado.keys())}")
        
        return {
            "score_mercado": float(mercado["score_consolidado"]),
            "mvrv": float(mercado["composicao"]["breakdown"]["ciclos"]["indicadores"]["MVRV_Z"]["valor"]),
            "nupl": float(mercado["composicao"]["breakdown"]["ciclos"]["indicadores"]["NUPL"]["valor"]),
            "classificacao_mercado": mercado["classificacao"]
        }
    except Exception as e:
        logger.error(f"❌ Erro dados mercado: {str(e)}")
        raise

def _get_risco_data() -> Dict:
    """Coleta dados de risco"""
    try:
        risco = calcular_analise_risco()
        if risco["status"] != "success":
            raise Exception(f"Análise risco falhou: {risco.get('erro')}")
        
        logger.info(f"🔍 Estrutura risco: {list(risco.keys())}")
        
        return {
            "score_risco": float(risco["score_consolidado"]),
            "health_factor": float(risco["composicao"]["breakdown"]["health_factor"]["valor_numerico"]),
            "dist_liquidacao": float(risco["composicao"]["breakdown"]["dist_liquidacao"]["valor_numerico"]),
            "classificacao_risco": risco["classificacao"]
        }
    except Exception as e:
        logger.error(f"❌ Erro dados risco: {str(e)}")
        raise

def _get_alavancagem_data() -> Dict:
    """Coleta dados de alavancagem"""
    try:
        alav = calcular_analise_alavancagem()
        if alav["status"] != "success":
            raise Exception(f"Análise alavancagem falhou: {alav.get('erro')}")
        
        situacao = alav["situacao_atual"]
        return {
            "alavancagem_atual": _extract_numeric(situacao["alavancagem_atual"]),
            "alavancagem_permitida": _extract_numeric(situacao["alavancagem_permitida"]),
            "valor_disponivel": _extract_monetary(situacao["valor_disponivel"]),
            "valor_a_reduzir": _extract_monetary(situacao["valor_a_reduzir"]),
            "posicao_total": _extract_monetary(situacao.get("posicao_total", "$0.00")),
            "status_alavancagem": situacao["status"]
        }
    except Exception as e:
        logger.error(f"❌ Erro dados alavancagem: {str(e)}")
        raise

def _get_technical_data() -> Dict:
    """Coleta dados técnicos do TradingView"""
    try:
        # EMA144 distance (REUTILIZA função existente)
        ema_distance = get_ema144_distance()
        
        # RSI diário (REUTILIZA função existente)
        rsi_diario = get_rsi_current(
            symbol="BTCUSDT",
            exchange="BINANCE", 
            timeframe=Interval.in_daily,
            period=14
        )
        
        # Preço atual e EMA144 valor
        price_data = _get_btc_price_and_ema()
        
        return {
            "ema_distance": float(ema_distance),
            "rsi_diario": float(rsi_diario),
            "btc_price": price_data["price"],
            "ema_valor": price_data["ema_144"]
        }
    except Exception as e:
        logger.error(f"❌ Erro dados técnicos: {str(e)}")
        raise

def _get_btc_price_and_ema() -> Dict:
    """Busca preço BTC atual e valor EMA144"""
    try:
        # REUTILIZA função existente do TradingView
        df = fetch_ohlc_data(
            symbol="BTCUSDT",
            exchange="BINANCE",
            interval=Interval.in_daily,
            n_bars=200  # Suficiente para EMA144
        )
        
        from app.services.utils.helpers.tradingview.tradingview_helper import calculate_ema
        
        # Calcular EMA144
        ema_144 = calculate_ema(df['close'], period=144)
        
        return {
            "price": float(df['close'].iloc[-1]),
            "ema_144": float(ema_144.iloc[-1])
        }
    except Exception as e:
        logger.error(f"❌ Erro preço/EMA: {str(e)}")
        raise

def _extract_numeric(value_str: str) -> float:
    """Extrai valor numérico de string (ex: '1.8x' -> 1.8)"""
    if isinstance(value_str, str):
        return float(value_str.replace("x", ""))
    return float(value_str) if value_str else 0.0

def _extract_monetary(value_str: str) -> float:
    """Extrai valor monetário de string (ex: '$1,500.00' -> 1500.0)"""
    if isinstance(value_str, str):
        return float(value_str.replace("$", "").replace(",", ""))
    return float(value_str) if value_str else 0.0

def _log_data_summary(data: Dict) -> None:
    """Log resumo dos dados coletados"""
    logger.info(f"📊 BTC: ${data['btc_price']:,.2f} | EMA144: {data['ema_distance']:+.1f}%")
    logger.info(f"📈 Scores - Mercado: {data['score_mercado']:.1f} | Risco: {data['score_risco']:.1f}")
    logger.info(f"⚡ Alavancagem: {data['alavancagem_atual']:.1f}x/{data['alavancagem_permitida']:.1f}x")
    logger.info(f"🔍 RSI: {data['rsi_diario']:.1f} | HF: {data['health_factor']:.2f}")