# app/services/dashboards/dash_main/analise_tatica/setups/cruzamento_medias.py

import logging
from typing import Dict, Any
from app.services.utils.helpers.tradingview.tradingview_helper import fetch_ohlc_data, calculate_ema
from tvDatafeed import Interval

logger = logging.getLogger(__name__)

def detectar_cruzamento_medias() -> Dict[str, Any]:
    """
    Detecta setup CRUZAMENTO DE MÉDIAS 4H
    
    Condições:
    - EMA17 cruza EMA34 de baixo para cima
    - Timeframe 4H para análise tática
    
    Returns:
        Dict com resultado da detecção
    """
    try:
        logger.info("🔍 Detectando Cruzamento de Médias 4H...")
        
        # 1. BUSCAR DADOS E CALCULAR EMAs
        emas_data = _obter_emas_4h()
        ema_17_atual = emas_data['ema_17_atual']
        ema_34_atual = emas_data['ema_34_atual']
        ema_17_anterior = emas_data['ema_17_anterior']
        ema_34_anterior = emas_data['ema_34_anterior']
        
        logger.info(f"📊 EMA17 atual: ${ema_17_atual:,.2f}, anterior: ${ema_17_anterior:,.2f}")
        logger.info(f"📊 EMA34 atual: ${ema_34_atual:,.2f}, anterior: ${ema_34_anterior:,.2f}")
        
        # 2. VALIDAR CONDIÇÕES DE CRUZAMENTO
        # Condição: EMA17 cruza EMA34 de baixo para cima
        cruzamento_ocorreu = (ema_17_atual > ema_34_atual) and (ema_17_anterior < ema_34_anterior)
        
        # Log detalhado das condições
        logger.info(f"🔍 EMA17 > EMA34 atual: {ema_17_atual > ema_34_atual} ({ema_17_atual:.2f} > {ema_34_atual:.2f})")
        logger.info(f"🔍 EMA17 < EMA34 anterior: {ema_17_anterior < ema_34_anterior} ({ema_17_anterior:.2f} < {ema_34_anterior:.2f})")
        logger.info(f"🔍 Cruzamento detectado: {cruzamento_ocorreu}")
        
        if cruzamento_ocorreu:
            logger.info("✅ CRUZAMENTO DE MÉDIAS identificado!")
            
            # Calcular força do setup baseado na diferença entre EMAs
            forca = _calcular_forca_setup(ema_17_atual, ema_34_atual)
            
            return {
                "encontrado": True,
                "setup": "CRUZAMENTO_MEDIAS",
                "forca": forca,
                "tamanho_posicao": 25,
                "dados_tecnicos": {
                    "ema_17": ema_17_atual,
                    "ema_34": ema_34_atual,
                    "ema_17_anterior": ema_17_anterior,
                    "ema_34_anterior": ema_34_anterior
                },
                "condicoes": {
                    "ema_17_atual": ema_17_atual,
                    "ema_34_atual": ema_34_atual,
                    "cruzamento": "EMA17 > EMA34 (atual) e EMA17 < EMA34 (anterior)"
                },
                "detalhes": f"Cruzamento médias: EMA17 ${ema_17_atual:,.2f} cruzou EMA34 ${ema_34_atual:,.2f}"
            }
        else:
            logger.info("❌ Cruzamento de Médias não identificado")
            return {
                "encontrado": False,
                "setup": "CRUZAMENTO_MEDIAS",
                "dados_tecnicos": {
                    "ema_17": ema_17_atual,
                    "ema_34": ema_34_atual,
                    "ema_17_anterior": ema_17_anterior,
                    "ema_34_anterior": ema_34_anterior
                },
                "detalhes": f"Condições não atendidas: cruzamento={cruzamento_ocorreu}"
            }
        
    except Exception as e:
        logger.error(f"❌ Erro Cruzamento de Médias: {str(e)}")
        return {
            "encontrado": False,
            "setup": "CRUZAMENTO_MEDIAS",
            "dados_tecnicos": {},
            "detalhes": f"Erro: {str(e)}"
        }

def _obter_emas_4h() -> Dict[str, float]:
    """Obtém EMAs 17 e 34 para timeframe 4H (atual e anterior)"""
    try:
        # Buscar dados 4H com barras suficientes
        df = fetch_ohlc_data(
            symbol="BTCUSDT",
            exchange="BINANCE", 
            interval=Interval.in_4_hour,
            n_bars=100  # Suficiente para EMA34 + buffer
        )
        
        # Calcular EMAs 17 e 34
        ema_17 = calculate_ema(df['close'], period=17)
        ema_34 = calculate_ema(df['close'], period=34)
        
        # Valores atuais (última barra)
        ema_17_atual = float(ema_17.iloc[-1])
        ema_34_atual = float(ema_34.iloc[-1])
        
        # Valores anteriores (penúltima barra)
        ema_17_anterior = float(ema_17.iloc[-2])
        ema_34_anterior = float(ema_34.iloc[-2])
        
        # Validações básicas
        if any(v <= 0 for v in [ema_17_atual, ema_34_atual, ema_17_anterior, ema_34_anterior]):
            raise ValueError("EMAs com valores inválidos")
        
        return {
            "ema_17_atual": ema_17_atual,
            "ema_34_atual": ema_34_atual,
            "ema_17_anterior": ema_17_anterior,
            "ema_34_anterior": ema_34_anterior
        }
        
    except Exception as e:
        logger.error(f"❌ Erro EMAs 4H: {str(e)}")
        raise Exception(f"EMAs 4H indisponíveis: {str(e)}")

def _calcular_forca_setup(ema_17: float, ema_34: float) -> str:
    """Calcula força do setup baseado na diferença percentual entre EMAs"""
    # Diferença percentual: quanto EMA17 está acima da EMA34
    diferenca_percent = ((ema_17 - ema_34) / ema_34) * 100
    
    # Quanto maior a diferença, mais forte o cruzamento
    if diferenca_percent > 1.0:
        return "muito_alta"
    elif diferenca_percent > 0.5:
        return "alta"
    elif diferenca_percent > 0.1:
        return "media"
    else:
        return "baixa"