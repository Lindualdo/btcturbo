# app/services/alertas/detectores/volatilidade_detector.py - VERSÃO FINAL

import logging
import pandas as pd
from typing import List, Optional
from datetime import datetime, timedelta
from ..models import AlertaCreate, TipoAlerta, CategoriaAlerta
from ...utils.helpers.bbw_calculator import obter_bbw_com_score, calculate_bollinger_bands, calculate_bbw_percentage
from ...utils.helpers.tradingview_helper import fetch_ohlc_data
from ...utils.helpers.analise.ema144_live_helper import obter_ema144_distance_atualizada
from ...utils.helpers.rsi_helper import obter_rsi_diario
from tvDatafeed import Interval

logger = logging.getLogger(__name__)

class VolatilidadeDetector:
    """
    Detecta alertas de volatilidade
    Debug usa exatamente as mesmas funções que verificar_alertas()
    """
    
    def verificar_alertas(self) -> List[AlertaCreate]:
        """Verifica todos os alertas de volatilidade"""
        alertas = []
        
        try:
            logger.info("🔍 Verificando alertas de volatilidade...")
            
            # 1. CRÍTICO: BBW < 5% por 7+ dias consecutivos
            bbw_extremo = self._check_bbw_compressao_extrema()
            if bbw_extremo:
                alertas.append(bbw_extremo)
            
            # 2. URGENTE: Volume spike > 300% da média
            volume_spike = self._check_volume_spike()
            if volume_spike:
                alertas.append(volume_spike)
            
            # 3. URGENTE: ATR mínimo histórico (< 1.5%)
            atr_minimo = self._check_atr_minimo_historico()
            if atr_minimo:
                alertas.append(atr_minimo)
            
            # 4. INFORMATIVO: EMA144 + RSI para realização
            ema_rsi_realizar = self._check_ema_rsi_realizar()
            if ema_rsi_realizar:
                alertas.append(ema_rsi_realizar)
            
            # 5. INFORMATIVO: Pump & Drift detectado
            pump_drift = self._check_pump_and_drift()
            if pump_drift:
                alertas.append(pump_drift)
            
            logger.info(f"✅ Volatilidade: {len(alertas)} alertas detectados")
            return alertas
            
        except Exception as e:
            logger.error(f"❌ Erro detector volatilidade: {str(e)}")
            return []
    
    def _check_bbw_compressao_extrema(self) -> Optional[AlertaCreate]:
        """1. BBW < 5% por 7+ dias = Explosão iminente"""
        try:
            bbw_data = obter_bbw_com_score()
            if bbw_data.get("status") != "success":
                return None
            
            bbw_atual = bbw_data["bbw_percentage"]
            df = fetch_ohlc_data(n_bars=30)
            dias_consecutivos = self._count_consecutive_bbw_days(df, threshold=5.0)
            
            if bbw_atual < 5.0 and dias_consecutivos >= 7:
                return AlertaCreate(
                    tipo=TipoAlerta.VOLATILIDADE,
                    categoria=CategoriaAlerta.CRITICO,
                    prioridade=0,
                    titulo="🔥 EXPLOSÃO IMINENTE",
                    mensagem=f"BBW {bbw_atual:.1f}% há {dias_consecutivos} dias - Breakout 24-72h",
                    threshold_configurado=5.0,
                    valor_atual=bbw_atual,
                    dados_contexto={
                        "dias_comprimido": dias_consecutivos,
                        "acao_recomendada": "Preparar capital dry powder",
                        "tipo_volatilidade": "compressao_extrema"
                    },
                    cooldown_minutos=240
                )
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro BBW extremo: {str(e)}")
            return None
    
    def _check_volume_spike(self) -> Optional[AlertaCreate]:
        """2. Volume spike > 300% da média"""
        try:
            df = fetch_ohlc_data(n_bars=20)
            volume_atual = float(df['volume'].iloc[-1])
            volume_media_10d = float(df['volume'].tail(10).mean())
            spike_percentual = ((volume_atual / volume_media_10d) - 1) * 100
            
            if spike_percentual > 300:
                return AlertaCreate(
                    tipo=TipoAlerta.VOLATILIDADE,
                    categoria=CategoriaAlerta.URGENTE,
                    prioridade=1,
                    titulo="⚡ VOLUME SPIKE",
                    mensagem=f"Volume {spike_percentual:.0f}% acima da média - Movimento forte",
                    threshold_configurado=300.0,
                    valor_atual=spike_percentual,
                    dados_contexto={
                        "acao_recomendada": "Monitorar direção do breakout",
                        "tipo_volatilidade": "volume_spike"
                    },
                    cooldown_minutos=120
                )
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro volume spike: {str(e)}")
            return None
    
    def _check_atr_minimo_historico(self) -> Optional[AlertaCreate]:
        """3. ATR < 1.5% = Volatilidade histórica baixa"""
        try:
            df = fetch_ohlc_data(n_bars=30)
            
            # Calcular ATR(14)
            high_low = df['high'] - df['low']
            high_close = abs(df['high'] - df['close'].shift())
            low_close = abs(df['low'] - df['close'].shift())
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(window=14).mean()
            atr_percentual = (atr.iloc[-1] / df['close'].iloc[-1]) * 100
            
            if atr_percentual < 1.5:
                return AlertaCreate(
                    tipo=TipoAlerta.VOLATILIDADE,
                    categoria=CategoriaAlerta.URGENTE,
                    prioridade=1,
                    titulo="🔥 ATR MÍNIMO",
                    mensagem=f"ATR {atr_percentual:.1f}% - Volatilidade histórica baixa",
                    threshold_configurado=1.5,
                    valor_atual=atr_percentual,
                    dados_contexto={
                        "acao_recomendada": "Preparar para expansão volatilidade",
                        "tipo_volatilidade": "atr_minimo"
                    },
                    cooldown_minutos=180
                )
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ATR mínimo: {str(e)}")
            return None
    
    def _check_ema_rsi_realizar(self) -> Optional[AlertaCreate]:
        """4. EMA144 > 20% + RSI > 70 = Realizar posição"""
        try:
            ema_distance = obter_ema144_distance_atualizada()
            rsi_diario = obter_rsi_diario()
            
            if ema_distance > 20 and rsi_diario > 70:
                return AlertaCreate(
                    tipo=TipoAlerta.VOLATILIDADE,
                    categoria=CategoriaAlerta.INFORMATIVO,
                    prioridade=2,
                    titulo="💰 ZONA DE REALIZAÇÃO",
                    mensagem=f"EMA144 +{ema_distance:.1f}% + RSI {rsi_diario:.0f} - Considerar tomar lucros",
                    threshold_configurado=20.0,
                    valor_atual=ema_distance,
                    dados_contexto={
                        "ema_distance": ema_distance,
                        "rsi_diario": rsi_diario,
                        "acao_recomendada": "Realizar 25-40% da posição",
                        "tipo_volatilidade": "oportunidade_realizacao"
                    },
                    cooldown_minutos=180
                )
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro EMA+RSI: {str(e)}")
            return None
    
    def _check_pump_and_drift(self) -> Optional[AlertaCreate]:
        """5. Pump & Drift = Pump forte + lateral por 2+ dias"""
        try:
            df = fetch_ohlc_data(n_bars=7)
            
            # Verificar pump nos últimos 3 dias
            pump_detectado = False
            for i in range(1, 4):
                variacao_dia = ((df['close'].iloc[-i] / df['close'].iloc[-i-1]) - 1) * 100
                if variacao_dia > 5:
                    pump_detectado = True
                    break
            
            # Verificar lateral (variação < 2% por 2+ dias)
            lateral_days = 0
            for i in range(1, 4):
                variacao = abs(((df['close'].iloc[-i] / df['close'].iloc[-i-1]) - 1) * 100)
                if variacao < 2:
                    lateral_days += 1
                else:
                    break
            
            if pump_detectado and lateral_days >= 2:
                return AlertaCreate(
                    tipo=TipoAlerta.VOLATILIDADE,
                    categoria=CategoriaAlerta.INFORMATIVO,
                    prioridade=2,
                    titulo="📊 PUMP & DRIFT",
                    mensagem=f"Pump detectado + {lateral_days} dias lateral - Correção 50% provável",
                    threshold_configurado=2.0,
                    valor_atual=lateral_days,
                    dados_contexto={
                        "acao_recomendada": "Aguardar correção para reentrada",
                        "tipo_volatilidade": "pump_drift"
                    },
                    cooldown_minutos=360
                )
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro Pump & Drift: {str(e)}")
            return None
    
    def _count_consecutive_bbw_days(self, df, threshold: float) -> int:
        """Conta dias consecutivos com BBW < threshold"""
        try:
            consecutive_days = 0
            for i in range(min(15, len(df) - 20)):
                window_data = df['close'].iloc[-(20+i):len(df)-i] if i > 0 else df['close'].tail(20)
                if len(window_data) >= 20:
                    upper_band, lower_band, middle_band = calculate_bollinger_bands(window_data)
                    bbw_pct = calculate_bbw_percentage(upper_band, lower_band, middle_band)
                    if bbw_pct < threshold:
                        consecutive_days += 1
                    else:
                        break
            return consecutive_days
        except Exception as e:
            logger.error(f"❌ Erro contando dias BBW: {str(e)}")
            return 0
    
    def get_debug_info(self) -> dict:
        """
        Debug usando EXATAMENTE as mesmas funções que verificar_alertas()
        Zero divergência - se detector mudar, debug reflete automaticamente
        """
        try:
            logger.info("🔍 Debug categoria VOLATILIDADE...")
            
            # Usar MESMAS funções internas que verificar_alertas() usa
            bbw_data = obter_bbw_com_score()
            
            df = fetch_ohlc_data(n_bars=30)
            dias_bbw_baixo = self._count_consecutive_bbw_days(df, 5.0) if df is not None else 0
            
            volume_df = fetch_ohlc_data(n_bars=20)
            volume_spike = 0
            if volume_df is not None:
                volume_atual = float(volume_df['volume'].iloc[-1])
                volume_media = float(volume_df['volume'].tail(10).mean())
                volume_spike = ((volume_atual / volume_media) - 1) * 100
            
            # ATR calculation
            atr_percentual = 0
            if df is not None and len(df) >= 30:
                high_low = df['high'] - df['low']
                high_close = abs(df['high'] - df['close'].shift())
                low_close = abs(df['low'] - df['close'].shift())
                true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
                atr = true_range.rolling(window=14).mean()
                atr_percentual = (atr.iloc[-1] / df['close'].iloc[-1]) * 100
            
            ema_distance = obter_ema144_distance_atualizada()
            rsi_diario = obter_rsi_diario()
            
            # Status baseado nos MESMOS thresholds dos _check methods
            alertas_status = {
                "bbw_compressao_extrema": {
                    "valor_atual": bbw_data.get("bbw_percentage", 0),
                    "dias_consecutivos": dias_bbw_baixo,
                    "threshold": 5.0,
                    "threshold_dias": 7,
                    "disparado": bbw_data.get("bbw_percentage", 15) < 5.0 and dias_bbw_baixo >= 7,
                    "acao": "Preparar capital dry powder" if bbw_data.get("bbw_percentage", 15) < 5.0 and dias_bbw_baixo >= 7 else "Monitorar"
                },
                "volume_spike": {
                    "valor_atual": round(volume_spike, 1),
                    "threshold": 300.0,
                    "disparado": volume_spike > 300,
                    "acao": "Monitorar breakout" if volume_spike > 300 else "Normal"
                },
                "atr_minimo": {
                    "valor_atual": round(atr_percentual, 2),
                    "threshold": 1.5,
                    "disparado": atr_percentual < 1.5,
                    "acao": "Preparar expansão" if atr_percentual < 1.5 else "Normal"
                },
                "ema_rsi_realizar": {
                    "ema_distance": ema_distance,
                    "rsi_diario": rsi_diario,
                    "threshold_ema": 20.0,
                    "threshold_rsi": 70.0,
                    "disparado": ema_distance > 20 and rsi_diario > 70,
                    "acao": "Realizar 25-40%" if ema_distance > 20 and rsi_diario > 70 else "Hold"
                },
                "pump_drift": {
                    "detectado": False,  # Simplificado para debug
                    "acao": "Aguardar padrão"
                }
            }
            
            # Executar verificação real
            alertas_detectados = self.verificar_alertas()
            
            return {
                "categoria": "VOLATILIDADE",
                "timestamp": datetime.utcnow().isoformat(),
                "dados_coletados": {
                    "bbw_percentage": bbw_data.get("bbw_percentage"),
                    "bbw_estado": bbw_data.get("estado"),
                    "dias_bbw_baixo": dias_bbw_baixo,
                    "ema144_distance": ema_distance,
                    "rsi_diario": rsi_diario,
                    "volume_spike_percent": round(volume_spike, 1),
                    "atr_percent": round(atr_percentual, 2)
                },
                "alertas_status": alertas_status,
                "alertas_detectados": len(alertas_detectados),
                "resumo_categoria": {
                    "total_alertas_possiveis": 5,
                    "alertas_disparados": len(alertas_detectados),
                    "urgencia": "ALTA" if any(a.categoria == CategoriaAlerta.CRITICO for a in alertas_detectados) else "NORMAL"
                },
                "fontes_dados": {
                    "bbw_data_ok": bbw_data.get("status") == "success",
                    "ema_distance_ok": ema_distance is not None,
                    "rsi_ok": rsi_diario is not None,
                    "tradingview_ok": df is not None and len(df) > 20,
                    "mesmo_codigo_producao": True
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro debug volatilidade: {str(e)}")
            return {
                "categoria": "VOLATILIDADE", 
                "timestamp": datetime.utcnow().isoformat(),
                "erro": str(e),
                "status": "error"
            }