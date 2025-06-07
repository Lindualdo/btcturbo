# app/services/alertas/detectores/volatilidade_detector.py - CORRIGIDO

import logging
import pandas as pd
from typing import List, Optional
from datetime import datetime, timedelta
from ..models import AlertaCreate, TipoAlerta, CategoriaAlerta
from ...utils.helpers.tradingview_helper import fetch_ohlc_data, calculate_bollinger_bands
from ...utils.helpers.bbw_calculator import calculate_bbw_percentage
from ...utils.helpers.analise.ema144_live_helper import obter_ema144_distance_atualizada
from ...utils.helpers.rsi_helper import obter_rsi_diario
from tvDatafeed import Interval

logger = logging.getLogger(__name__)

class VolatilidadeDetector:
    """
    Detecta alertas de volatilidade e timing
    CORRIGIDO: Usa TradingView para BBW histórico
    """
    
    def verificar_alertas(self) -> List[AlertaCreate]:
        """Verifica alertas de volatilidade"""
        alertas = []
        
        try:
            # 1. CRÍTICO: BBW < 5% por 7+ dias
            bbw_alert = self._check_bbw_compressao_extrema()
            if bbw_alert:
                alertas.append(bbw_alert)
            
            # 2. TÁTICO: EMA144 > 20% + RSI > 70
            ema_rsi_alert = self._check_ema_rsi_realizar()
            if ema_rsi_alert:
                alertas.append(ema_rsi_alert)
            
            # 3. INFORMATIVO: BBW normal após compressão
            bbw_normal = self._check_bbw_expandindo()
            if bbw_normal:
                alertas.append(bbw_normal)
            
            logger.info(f"✅ Volatilidade: {len(alertas)} alertas detectados")
            return alertas
            
        except Exception as e:
            logger.error(f"❌ Erro detector volatilidade: {str(e)}")
            return []
    
    def _check_bbw_compressao_extrema(self) -> Optional[AlertaCreate]:
        """CORRIGIDO: BBW < 5% por 7+ dias usando TradingView"""
        try:
            logger.info("🔍 Verificando BBW compressão extrema...")
            
            # Buscar dados históricos (30 dias)
            df = fetch_ohlc_data(
                symbol="BTCUSDT",
                exchange="BINANCE", 
                interval=Interval.in_daily,
                n_bars=30
            )
            
            # Calcular BBW para cada dia
            bbw_series = []
            for i in range(20, len(df)):  # Precisamos 20 períodos para BB
                window_data = df['close'].iloc[i-19:i+1]
                bands = calculate_bollinger_bands(window_data, period=20, std_dev=2.0)
                
                upper = bands['upper'].iloc[-1]
                lower = bands['lower'].iloc[-1] 
                middle = bands['middle'].iloc[-1]
                
                bbw_pct = calculate_bbw_percentage(upper, lower, middle)
                bbw_series.append({
                    'date': df.index[i],
                    'bbw': bbw_pct
                })
            
            # Contar dias consecutivos < 5%
            dias_consecutivos = self._count_consecutive_bbw_days(bbw_series, 5.0)
            bbw_atual = bbw_series[-1]['bbw'] if bbw_series else 15.0
            
            logger.info(f"📊 BBW atual: {bbw_atual:.1f}%, dias consecutivos < 5%: {dias_consecutivos}")
            
            if bbw_atual < 5.0 and dias_consecutivos >= 7:
                return AlertaCreate(
                    tipo=TipoAlerta.VOLATILIDADE,
                    categoria=CategoriaAlerta.CRITICO,
                    prioridade=0,
                    titulo="🔥 EXPLOSÃO IMINENTE",
                    mensagem=f"BBW {bbw_atual:.1f}% há {dias_consecutivos} dias - Breakout iminente",
                    threshold_configurado=5.0,
                    valor_atual=bbw_atual,
                    dados_contexto={
                        "dias_comprimido": dias_consecutivos,
                        "acao_recomendada": "Preparar capital para breakout",
                        "historico": "Compressão extrema detectada",
                        "timeframe": "24-72h"
                    },
                    cooldown_minutos=240
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro check BBW extremo: {str(e)}")
            return None
    
    def _count_consecutive_bbw_days(self, bbw_series: List[dict], threshold: float) -> int:
        """Conta dias consecutivos com BBW abaixo do threshold"""
        try:
            if not bbw_series:
                return 0
            
            consecutive_days = 0
            
            # Contar do mais recente para trás
            for i in range(len(bbw_series) - 1, -1, -1):
                if bbw_series[i]['bbw'] < threshold:
                    consecutive_days += 1
                else:
                    break
            
            return consecutive_days
            
        except Exception as e:
            logger.error(f"❌ Erro contando dias consecutivos: {str(e)}")
            return 0
    
    def _check_ema_rsi_realizar(self) -> Optional[AlertaCreate]:
        """EMA144 > 20% + RSI > 70 = Realizar 40%"""
        try:
            logger.info("🔍 Verificando EMA144 + RSI para realização...")
            
            ema_distance = obter_ema144_distance_atualizada()
            rsi_diario = obter_rsi_diario()
            
            logger.info(f"📊 EMA144: {ema_distance:+.1f}%, RSI: {rsi_diario:.1f}")
            
            if ema_distance > 20 and rsi_diario > 70:
                return AlertaCreate(
                    tipo=TipoAlerta.VOLATILIDADE,
                    categoria=CategoriaAlerta.URGENTE,
                    prioridade=1,
                    titulo="💰 REALIZAR POSIÇÃO",
                    mensagem=f"EMA144 +{ema_distance:.1f}% + RSI {rsi_diario:.0f} - Tomar 40%",
                    threshold_configurado=20.0,
                    valor_atual=ema_distance,
                    dados_contexto={
                        "ema_distance": ema_distance,
                        "rsi_diario": rsi_diario,
                        "acao_recomendada": "Realizar 40% da posição",
                        "justificativa": "Extremo sobrecomprado",
                        "matriz_tatica": "Regra EMA144 + RSI"
                    },
                    cooldown_minutos=120
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro check EMA+RSI: {str(e)}")
            return None
    
    def _check_bbw_expandindo(self) -> Optional[AlertaCreate]:
        """BBW voltando ao normal após compressão"""
        try:
            logger.info("🔍 Verificando BBW expandindo...")
            
            # Buscar BBW atual
            df = fetch_ohlc_data(n_bars=25)
            recent_data = df['close'].tail(20)
            bands = calculate_bollinger_bands(recent_data)
            
            upper = bands['upper'].iloc[-1]
            lower = bands['lower'].iloc[-1]
            middle = bands['middle'].iloc[-1]
            bbw_atual = calculate_bbw_percentage(upper, lower, middle)
            
            # Verificar se houve compressão nos últimos 5 dias
            compressao_recente = False
            for i in range(5, 10):  # Dias 5-10 atrás
                window = df['close'].iloc[-20-i:-i] if i > 0 else df['close'].tail(20)
                if len(window) >= 20:
                    bands_hist = calculate_bollinger_bands(window)
                    bbw_hist = calculate_bbw_percentage(
                        bands_hist['upper'].iloc[-1],
                        bands_hist['lower'].iloc[-1], 
                        bands_hist['middle'].iloc[-1]
                    )
                    if bbw_hist < 6.0:
                        compressao_recente = True
                        break
            
            if 8 <= bbw_atual <= 15 and compressao_recente:
                return AlertaCreate(
                    tipo=TipoAlerta.VOLATILIDADE,
                    categoria=CategoriaAlerta.INFORMATIVO,
                    prioridade=2,
                    titulo="📊 BBW EXPANDINDO",
                    mensagem=f"BBW {bbw_atual:.1f}% - Volatilidade normalizando",
                    threshold_configurado=8.0,
                    valor_atual=bbw_atual,
                    dados_contexto={
                        "acao_recomendada": "Monitorar direção do movimento",
                        "status": "Saindo da compressão"
                    },
                    cooldown_minutos=360
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro check BBW expandindo: {str(e)}")
            return None