# app/services/alertas/detectores/volatilidade_detector.py - CORRIGIDO

import logging
import pandas as pd
from typing import List, Optional
from datetime import datetime, timedelta
from ..models import AlertaCreate, TipoAlerta, CategoriaAlerta
from ...utils.helpers.tradingview.bbw_calculator import calculate_bollinger_bands, calculate_bbw_percentage
from ...utils.helpers.tradingview.tradingview_helper import fetch_ohlc_data
from ...utils.helpers.analise.ema144_live_helper import obter_ema144_distance_atualizada
from ...utils.helpers.tradingview.rsi_helper import obter_rsi_diario
from tvDatafeed import Interval

logger = logging.getLogger(__name__)

class VolatilidadeDetector:
    """
    Detecta alertas de volatilidade - VERSÃO CORRIGIDA
    """
    
    def verificar_alertas(self) -> List[AlertaCreate]:
        """Verifica todos os alertas de volatilidade"""
        alertas = []
        
        try:
            logger.info("🔍 Verificando alertas de volatilidade...")
            
            # 1. CRÍTICO: BBW < 10% por 5+ dias (CORRIGIDO: threshold mais realista)
            bbw_extremo = self._check_bbw_compressao_extrema()
            if bbw_extremo:
                alertas.append(bbw_extremo)
            
            # 2. URGENTE: Volume spike > 200% (CORRIGIDO: threshold mais sensível)
            volume_spike = self._check_volume_spike()
            if volume_spike:
                alertas.append(volume_spike)
            
            # 3. URGENTE: ATR mínimo histórico (CORRIGIDO: cálculo sem NaN)
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
        """1. BBW < 10% por 5+ dias = Explosão iminente (CORRIGIDO)"""
        try:
            df = fetch_ohlc_data(n_bars=30)
            
            # CORRIGIDO: Calcular BBW atual corretamente
            upper_band, lower_band, middle_band = calculate_bollinger_bands(
                df['close'], period=20, std_dev=2.0
            )
            bbw_atual = calculate_bbw_percentage(upper_band, lower_band, middle_band)
            
            # CORRIGIDO: Contar dias consecutivos corretamente
            dias_consecutivos = self._count_consecutive_bbw_days_fixed(df, threshold=10.0)
            
            # CORRIGIDO: Threshold mais realista (10% ao invés de 5%)
            if bbw_atual < 10.0 and dias_consecutivos >= 5:
                return AlertaCreate(
                    tipo=TipoAlerta.VOLATILIDADE,
                    categoria=CategoriaAlerta.CRITICO,
                    prioridade=0,
                    titulo="🔥 SQUEEZE DETECTADO",
                    mensagem=f"BBW {bbw_atual:.1f}% há {dias_consecutivos} dias - Breakout 24-72h",
                    threshold_configurado=10.0,  # CORRIGIDO
                    valor_atual=bbw_atual,
                    dados_contexto={
                        "dias_comprimido": dias_consecutivos,
                        "acao_recomendada": "Preparar capital dry powder",
                        "tipo_volatilidade": "compressao_extrema",
                        "bbw_threshold": 10.0
                    },
                    cooldown_minutos=240
                )
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro BBW extremo: {str(e)}")
            return None
    
    def _check_volume_spike(self) -> Optional[AlertaCreate]:
        """2. Volume spike > 200% da média (CORRIGIDO: threshold mais sensível)"""
        try:
            df = fetch_ohlc_data(n_bars=20)
            
            # CORRIGIDO: Validar se existe coluna volume
            if 'volume' not in df.columns or df['volume'].isna().all():
                logger.warning("⚠️ Dados de volume indisponíveis")
                return None
            
            volume_atual = float(df['volume'].iloc[-1])
            volume_media_10d = float(df['volume'].tail(10).mean())
            
            # CORRIGIDO: Evitar divisão por zero
            if volume_media_10d <= 0:
                logger.warning("⚠️ Volume médio inválido")
                return None
            
            spike_percentual = ((volume_atual / volume_media_10d) - 1) * 100
            
            # CORRIGIDO: Threshold mais sensível (200% ao invés de 300%)
            if spike_percentual > 200:
                return AlertaCreate(
                    tipo=TipoAlerta.VOLATILIDADE,
                    categoria=CategoriaAlerta.URGENTE,
                    prioridade=1,
                    titulo="⚡ VOLUME SPIKE",
                    mensagem=f"Volume {spike_percentual:.0f}% acima da média - Movimento forte",
                    threshold_configurado=200.0,  # CORRIGIDO
                    valor_atual=spike_percentual,
                    dados_contexto={
                        "volume_atual": volume_atual,
                        "volume_media": volume_media_10d,
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
        """3. ATR < 2.0% = Volatilidade histórica baixa (CORRIGIDO: sem NaN)"""
        try:
            df = fetch_ohlc_data(n_bars=30)
            
            # CORRIGIDO: Calcular ATR sem NaN
            high_low = df['high'] - df['low']
            high_close = abs(df['high'] - df['close'].shift()).fillna(0)  # CORRIGIDO: fillna
            low_close = abs(df['low'] - df['close'].shift()).fillna(0)    # CORRIGIDO: fillna
            
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            
            # CORRIGIDO: Garantir pelo menos 14 períodos válidos
            if len(true_range) < 14:
                logger.warning("⚠️ Dados insuficientes para ATR")
                return None
            
            atr = true_range.rolling(window=14).mean()
            atr_percentual = (atr.iloc[-1] / df['close'].iloc[-1]) * 100
            
            # CORRIGIDO: Threshold mais realista (2.0% ao invés de 1.5%)
            if atr_percentual < 2.0:
                return AlertaCreate(
                    tipo=TipoAlerta.VOLATILIDADE,
                    categoria=CategoriaAlerta.URGENTE,
                    prioridade=1,
                    titulo="🔥 ATR MÍNIMO",
                    mensagem=f"ATR {atr_percentual:.1f}% - Volatilidade histórica baixa",
                    threshold_configurado=2.0,  # CORRIGIDO
                    valor_atual=atr_percentual,
                    dados_contexto={
                        "atr_absoluto": float(atr.iloc[-1]),
                        "preco_atual": float(df['close'].iloc[-1]),
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
        """4. EMA144 > 15% + RSI > 65 = Realizar posição (CORRIGIDO: thresholds)"""
        try:
            ema_distance = obter_ema144_distance_atualizada()
            rsi_diario = obter_rsi_diario()
            
            # CORRIGIDO: Thresholds mais sensíveis
            if ema_distance > 15 and rsi_diario > 65:
                return AlertaCreate(
                    tipo=TipoAlerta.VOLATILIDADE,
                    categoria=CategoriaAlerta.INFORMATIVO,
                    prioridade=2,
                    titulo="💰 ZONA DE REALIZAÇÃO",
                    mensagem=f"EMA144 +{ema_distance:.1f}% + RSI {rsi_diario:.0f} - Considerar tomar lucros",
                    threshold_configurado=15.0,  # CORRIGIDO
                    valor_atual=ema_distance,
                    dados_contexto={
                        "ema_distance": ema_distance,
                        "rsi_diario": rsi_diario,
                        "acao_recomendada": "Realizar 25-40% da posição",
                        "tipo_volatilidade": "oportunidade_realizacao",
                        "thresholds": {"ema": 15.0, "rsi": 65.0}
                    },
                    cooldown_minutos=180
                )
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro EMA+RSI: {str(e)}")
            return None
    
    def _check_pump_and_drift(self) -> Optional[AlertaCreate]:
        """5. Pump & Drift = Pump forte + lateral por 2+ dias (CORRIGIDO)"""
        try:
            df = fetch_ohlc_data(n_bars=7)
            
            # CORRIGIDO: Verificar pump nos últimos 3 dias com threshold menor
            pump_detectado = False
            pump_day = None
            for i in range(1, 4):
                if len(df) > i:
                    variacao_dia = ((df['close'].iloc[-i] / df['close'].iloc[-i-1]) - 1) * 100
                    if variacao_dia > 3:  # CORRIGIDO: 3% ao invés de 5%
                        pump_detectado = True
                        pump_day = i
                        break
            
            # CORRIGIDO: Verificar lateral após pump
            lateral_days = 0
            if pump_detectado and pump_day:
                for i in range(1, pump_day):
                    if len(df) > i:
                        variacao = abs(((df['close'].iloc[-i] / df['close'].iloc[-i-1]) - 1) * 100)
                        if variacao < 1.5:  # CORRIGIDO: threshold mais rigoroso
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
                        "pump_day": pump_day,
                        "lateral_days": lateral_days,
                        "acao_recomendada": "Aguardar correção para reentrada",
                        "tipo_volatilidade": "pump_drift"
                    },
                    cooldown_minutos=360
                )
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro Pump & Drift: {str(e)}")
            return None
    
    def _count_consecutive_bbw_days_fixed(self, df: pd.DataFrame, threshold: float) -> int:
        """CORRIGIDO: Conta dias consecutivos com BBW < threshold"""
        try:
            consecutive_days = 0
            
            # CORRIGIDO: Iterar do mais recente para o mais antigo
            for days_back in range(1, min(15, len(df) - 20)):
                # Pegar janela de 20 dias terminando 'days_back' dias atrás
                end_idx = len(df) - days_back
                start_idx = end_idx - 20
                
                if start_idx >= 0:
                    window_data = df['close'].iloc[start_idx:end_idx]
                    
                    if len(window_data) >= 20:
                        upper_band, lower_band, middle_band = calculate_bollinger_bands(
                            window_data, period=20, std_dev=2.0
                        )
                        bbw_pct = calculate_bbw_percentage(upper_band, lower_band, middle_band)
                        
                        if bbw_pct < threshold:
                            consecutive_days += 1
                        else:
                            break
                    else:
                        break
                else:
                    break
            
            return consecutive_days
            
        except Exception as e:
            logger.error(f"❌ Erro contando dias BBW: {str(e)}")
            return 0
    
    def get_debug_info(self) -> dict:
        """Debug usando funções corrigidas"""
        try:
            logger.info("🔍 Debug categoria VOLATILIDADE (CORRIGIDO)...")
            
            # Usar mesmas funções corrigidas
            bbw_check = self._check_bbw_compressao_extrema()
            volume_check = self._check_volume_spike()
            atr_check = self._check_atr_minimo_historico()
            ema_rsi_check = self._check_ema_rsi_realizar()
            pump_drift_check = self._check_pump_and_drift()
            
            dados_coletados = {}
            alertas_status = {}
            
            # BBW - CORRIGIDO
            if bbw_check:
                dados_coletados["bbw_percentage"] = bbw_check.valor_atual
                dados_coletados["dias_bbw_baixo"] = bbw_check.dados_contexto.get("dias_comprimido")
                alertas_status["bbw_compressao"] = {
                    "valor_atual": bbw_check.valor_atual,
                    "threshold": bbw_check.threshold_configurado,
                    "disparado": True,
                    "acao": bbw_check.dados_contexto.get("acao_recomendada")
                }
            else:
                try:
                    df = fetch_ohlc_data(n_bars=30)
                    upper_band, lower_band, middle_band = calculate_bollinger_bands(
                        df['close'], period=20, std_dev=2.0
                    )
                    bbw_atual = calculate_bbw_percentage(upper_band, lower_band, middle_band)
                    dias_bbw = self._count_consecutive_bbw_days_fixed(df, 10.0)
                    
                    dados_coletados["bbw_percentage"] = bbw_atual
                    dados_coletados["dias_bbw_baixo"] = dias_bbw
                    alertas_status["bbw_compressao"] = {
                        "valor_atual": bbw_atual,
                        "threshold": 10.0,
                        "disparado": False,
                        "acao": "Monitorar"
                    }
                except Exception as e:
                    alertas_status["bbw_compressao"] = {
                        "disparado": False,
                        "acao": f"Erro: {str(e)[:50]}"
                    }
            
            # Volume - CORRIGIDO
            if volume_check:
                dados_coletados["volume_spike_percent"] = volume_check.valor_atual
                alertas_status["volume_spike"] = {
                    "valor_atual": volume_check.valor_atual,
                    "threshold": volume_check.threshold_configurado,
                    "disparado": True,
                    "acao": volume_check.dados_contexto.get("acao_recomendada")
                }
            else:
                try:
                    df = fetch_ohlc_data(n_bars=20)
                    if 'volume' in df.columns and not df['volume'].isna().all():
                        volume_atual = float(df['volume'].iloc[-1])
                        volume_media = float(df['volume'].tail(10).mean())
                        if volume_media > 0:
                            volume_spike = ((volume_atual / volume_media) - 1) * 100
                            dados_coletados["volume_spike_percent"] = round(volume_spike, 1)
                            alertas_status["volume_spike"] = {
                                "valor_atual": round(volume_spike, 1),
                                "threshold": 200.0,
                                "disparado": False,
                                "acao": "Normal"
                            }
                        else:
                            alertas_status["volume_spike"] = {"disparado": False, "acao": "Volume zero"}
                    else:
                        alertas_status["volume_spike"] = {"disparado": False, "acao": "Volume indisponível"}
                except Exception as e:
                    alertas_status["volume_spike"] = {"disparado": False, "acao": f"Erro: {str(e)[:50]}"}
            
            # ATR - CORRIGIDO
            if atr_check:
                dados_coletados["atr_percent"] = atr_check.valor_atual
                alertas_status["atr_minimo"] = {
                    "valor_atual": atr_check.valor_atual,
                    "threshold": atr_check.threshold_configurado,
                    "disparado": True,
                    "acao": atr_check.dados_contexto.get("acao_recomendada")
                }
            else:
                try:
                    df = fetch_ohlc_data(n_bars=30)
                    if len(df) >= 16:  # Mínimo para ATR14
                        high_low = df['high'] - df['low']
                        high_close = abs(df['high'] - df['close'].shift()).fillna(0)
                        low_close = abs(df['low'] - df['close'].shift()).fillna(0)
                        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
                        atr = true_range.rolling(window=14).mean()
                        atr_percentual = (atr.iloc[-1] / df['close'].iloc[-1]) * 100
                        
                        dados_coletados["atr_percent"] = round(atr_percentual, 2)
                        alertas_status["atr_minimo"] = {
                            "valor_atual": round(atr_percentual, 2),
                            "threshold": 2.0,
                            "disparado": False,
                            "acao": "Normal"
                        }
                    else:
                        alertas_status["atr_minimo"] = {"disparado": False, "acao": "Dados insuficientes"}
                except Exception as e:
                    alertas_status["atr_minimo"] = {"disparado": False, "acao": f"Erro: {str(e)[:50]}"}
            
            # EMA + RSI
            if ema_rsi_check:
                dados_coletados["ema144_distance"] = ema_rsi_check.dados_contexto.get("ema_distance")
                dados_coletados["rsi_diario"] = ema_rsi_check.dados_contexto.get("rsi_diario")
                alertas_status["ema_rsi_realizar"] = {
                    "ema_distance": ema_rsi_check.dados_contexto.get("ema_distance"),
                    "rsi_diario": ema_rsi_check.dados_contexto.get("rsi_diario"),
                    "disparado": True,
                    "acao": ema_rsi_check.dados_contexto.get("acao_recomendada")
                }
            else:
                try:
                    ema_distance = obter_ema144_distance_atualizada()
                    rsi_diario = obter_rsi_diario()
                    dados_coletados["ema144_distance"] = ema_distance
                    dados_coletados["rsi_diario"] = rsi_diario
                    alertas_status["ema_rsi_realizar"] = {
                        "ema_distance": ema_distance,
                        "rsi_diario": rsi_diario,
                        "threshold_ema": 15.0,
                        "threshold_rsi": 65.0,
                        "disparado": False,
                        "acao": "Hold"
                    }
                except Exception as e:
                    alertas_status["ema_rsi_realizar"] = {"disparado": False, "acao": f"Erro: {str(e)[:50]}"}
            
            # Pump & Drift
            if pump_drift_check:
                alertas_status["pump_drift"] = {
                    "valor_atual": pump_drift_check.valor_atual,
                    "disparado": True,
                    "acao": pump_drift_check.dados_contexto.get("acao_recomendada")
                }
            else:
                alertas_status["pump_drift"] = {"disparado": False, "acao": "Aguardar padrão"}
            
            alertas_detectados = [bbw_check, volume_check, atr_check, ema_rsi_check, pump_drift_check]
            alertas_ativos = [a for a in alertas_detectados if a is not None]
            
            return {
                "categoria": "VOLATILIDADE",
                "timestamp": datetime.utcnow().isoformat(),
                "versao": "CORRIGIDA",
                "correcoes_aplicadas": [
                    "BBW threshold: 5% → 10%",
                    "Volume spike: 300% → 200%", 
                    "ATR threshold: 1.5% → 2.0%",
                    "EMA+RSI: 20%/70 → 15%/65",
                    "Pump&Drift: 5% → 3%",
                    "ATR sem NaN",
                    "BBW dias consecutivos corrigido"
                ],
                "dados_coletados": dados_coletados,
                "alertas_status": alertas_status,
                "alertas_detectados": len(alertas_ativos),
                "resumo_categoria": {
                    "total_alertas_possiveis": 5,
                    "alertas_disparados": len(alertas_ativos),
                    "urgencia": "ALTA" if any(a and a.categoria == CategoriaAlerta.CRITICO for a in alertas_ativos) else "NORMAL"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro debug volatilidade: {str(e)}")
            return {
                "categoria": "VOLATILIDADE", 
                "timestamp": datetime.utcnow().isoformat(),
                "versao": "CORRIGIDA",
                "erro": str(e),
                "status": "error"
            }