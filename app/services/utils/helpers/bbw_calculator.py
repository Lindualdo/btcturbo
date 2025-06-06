# app/services/utils/helpers/bbw_calculator.py

import logging
import pandas as pd
import numpy as np
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

def calculate_bollinger_bands(prices: pd.Series, period: int = 20, std_dev: float = 2.0) -> Tuple[float, float, float]:
    """
    Calcula Bollinger Bands para série de preços
    
    Args:
        prices: Série de preços (close)
        period: Período para SMA (padrão 20)
        std_dev: Desvio padrão multiplicador (padrão 2.0)
    
    Returns:
        Tuple (upper_band, lower_band, middle_band)
    """
    try:
        if len(prices) < period:
            raise ValueError(f"Dados insuficientes: {len(prices)} < {period}")
        
        # Média móvel simples (middle band)
        sma = prices.rolling(window=period).mean()
        middle_band = float(sma.iloc[-1])
        
        # Desvio padrão
        std = prices.rolling(window=period).std()
        std_current = float(std.iloc[-1])
        
        # Bandas superior e inferior
        upper_band = middle_band + (std_dev * std_current)
        lower_band = middle_band - (std_dev * std_current)
        
        logger.info(f"✅ Bollinger Bands: Upper={upper_band:.2f}, Middle={middle_band:.2f}, Lower={lower_band:.2f}")
        
        return upper_band, lower_band, middle_band
        
    except Exception as e:
        logger.error(f"❌ Erro calculando Bollinger Bands: {str(e)}")
        raise

def calculate_bbw_percentage(upper_band: float, lower_band: float, middle_band: float) -> float:
    """
    Calcula Bollinger Band Width em percentual
    
    Formula: BBW% = ((Upper - Lower) / Middle) * 100
    
    Args:
        upper_band: Banda superior
        lower_band: Banda inferior  
        middle_band: Banda central (SMA)
    
    Returns:
        BBW em percentual
    """
    try:
        if middle_band <= 0:
            raise ValueError(f"Middle band inválida: {middle_band}")
        
        bbw_percentage = ((upper_band - lower_band) / middle_band) * 100
        
        # Validação: BBW deve estar entre 1% e 100%
        if not (1.0 <= bbw_percentage <= 100.0):
            logger.warning(f"⚠️ BBW fora do range esperado: {bbw_percentage:.2f}%")
        
        logger.info(f"📊 BBW calculado: {bbw_percentage:.2f}%")
        return round(bbw_percentage, 2)
        
    except Exception as e:
        logger.error(f"❌ Erro calculando BBW: {str(e)}")
        raise

def calculate_bbw_score(bbw_percentage: float) -> float:
    """
    Converte BBW% em score 0-10 conforme especificação
    
    Tabela de conversão:
    < 5%: Score 9-10 (volatilidade muito baixa - breakout iminente)
    5-10%: Score 7-8 (volatilidade baixa - acumulação)
    10-20%: Score 5-6 (volatilidade normal)
    20-30%: Score 3-4 (volatilidade alta)
    > 30%: Score 0-2 (volatilidade extrema)
    
    Args:
        bbw_percentage: BBW em percentual
    
    Returns:
        Score de 0 a 10
    """
    try:
        if bbw_percentage < 0:
            logger.warning(f"⚠️ BBW negativo: {bbw_percentage}% - usando 0")
            bbw_percentage = 0
        
        # Aplicar tabela de conversão
        if bbw_percentage < 5:
            # Volatilidade muito baixa - breakout iminente
            score = 9.5
            status = "muito_baixa"
        elif bbw_percentage < 10:
            # Volatilidade baixa - acumulação
            score = 7.5
            status = "baixa"
        elif bbw_percentage < 20:
            # Volatilidade normal
            score = 5.5
            status = "normal"
        elif bbw_percentage < 30:
            # Volatilidade alta
            score = 3.5
            status = "alta"
        else:
            # Volatilidade extrema
            score = 1.5
            status = "extrema"
        
        logger.info(f"🎯 BBW Score: {score}/10 (volatilidade {status} - {bbw_percentage:.2f}%)")
        
        return float(score)
        
    except Exception as e:
        logger.error(f"❌ Erro calculando score BBW: {str(e)}")
        return 5.0  # Score neutro em caso de erro

def get_bbw_interpretation(bbw_percentage: float) -> dict:
    """
    Retorna interpretação detalhada do BBW
    
    Args:
        bbw_percentage: BBW em percentual
    
    Returns:
        Dict com interpretação completa
    """
    score = calculate_bbw_score(bbw_percentage)
    
    interpretations = {
        "muito_baixa": {
            "status": "Compressão Extrema",
            "significado": "Breakout iminente - preparar posição",
            "acao": "Aguardar direção do breakout",
            "timeframe": "1-7 dias"
        },
        "baixa": {
            "status": "Acumulação",
            "significado": "Mercado em consolidação",
            "acao": "Posição neutra - aguardar sinais",
            "timeframe": "1-2 semanas"
        },
        "normal": {
            "status": "Volatilidade Normal",
            "significado": "Movimentação típica de mercado",
            "acao": "Seguir tendência principal",
            "timeframe": "Indefinido"
        },
        "alta": {
            "status": "Volatilidade Elevada",
            "significado": "Mercado agitado - cautela",
            "acao": "Reduzir alavancagem",
            "timeframe": "Alguns dias"
        },
        "extrema": {
            "status": "Caos de Mercado",
            "significado": "Volatilidade perigosa",
            "acao": "Evitar novas posições",
            "timeframe": "Até normalizar"
        }
    }
    
    # Determinar categoria
    if bbw_percentage < 5:
        category = "muito_baixa"
    elif bbw_percentage < 10:
        category = "baixa"
    elif bbw_percentage < 20:
        category = "normal"
    elif bbw_percentage < 30:
        category = "alta"
    else:
        category = "extrema"
    
    return {
        "bbw_percentage": bbw_percentage,
        "score": score,
        "categoria": category,
        **interpretations[category]
    }

def obter_bbw_com_score() -> dict:
    """
    NOVA FUNÇÃO: Obter BBW com score calculado
    Usada pela análise tática completa
    """
    try:
        from app.services.utils.helpers.tradingview_helper import fetch_ohlc_data, calculate_ema
        from tvDatafeed import Interval
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info("📊 Calculando BBW com score...")
        
        # Buscar dados para BBW
        df = fetch_ohlc_data(
            symbol="BTCUSDT",
            exchange="BINANCE",
            interval=Interval.in_daily,
            n_bars=30
        )
        
        # Calcular Bollinger Bands
        upper_band, lower_band, middle_band = calculate_bollinger_bands(
            df['close'], period=20, std_dev=2.0
        )
        
        # Calcular BBW%
        bbw_percentage = calculate_bbw_percentage(upper_band, lower_band, middle_band)
        
        # Calcular score BBW
        score_bbw = calculate_bbw_score(bbw_percentage)
        
        # Determinar estado
        if bbw_percentage < 5:
            estado = "compressao_extrema"
        elif bbw_percentage < 10:
            estado = "volatilidade_baixa"
        elif bbw_percentage < 20:
            estado = "volatilidade_normal"
        elif bbw_percentage < 30:
            estado = "volatilidade_alta"
        else:
            estado = "volatilidade_extrema"
        
        logger.info(f"✅ BBW: {bbw_percentage:.2f}% ({estado})")
        
        return {
            "bbw_percentage": bbw_percentage,
            "score_bbw": score_bbw,
            "estado": estado,
            "bands": {
                "upper": upper_band,
                "lower": lower_band,
                "middle": middle_band
            },
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro obtendo BBW: {str(e)}")
        return {
            "bbw_percentage": 15.0,  # Fallback neutro
            "score_bbw": 5.0,
            "estado": "erro",
            "status": "error",
            "erro": str(e)
        }