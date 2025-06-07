# app/services/alertas/detectores/volatilidade_detector.py - REFATORADO

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
    REFATORADO: Debug usa mesma lógica que produção
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
                        "historico_performance": "Últimas 5x = +/-15% avg em 3 dias",
                        "timeframe": "24-72h",
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
                        "volume_atual": volume_atual,
                        "volume_media": volume_media_10d,
                        "acao_recomendada": "Monitorar direção do breakout",
                        "timeframe": "Próximas 4-12h",
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
                        "significado": "Mercado comprimido - movimento iminente",
                        "timeframe": "1-7 dias",
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
                        "justificativa": "Extremo sobrecomprado",
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
                        "probabilidade_correcao": "50% nas próximas 48h",
                        "pattern": "Pump & Drift clássico",
                        "timeframe": "24-48h",
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
        REFATORADO: Debug usa mesma lógica que produção
        Executa verificar_alertas() e extrai dados dos alertas
        """
        try:
            logger.info("🔍 Debug categoria VOLATILIDADE...")
            
            # USAR MESMA FUNÇÃO QUE PRODUÇÃO
            alertas_detectados = self.verificar_alertas()
            alertas_volatilidade = [a for a in alertas_detectados if a.tipo == TipoAlerta.VOLATILIDADE]
            
            # Extrair dados dos alertas para debug
            dados_extraidos = self._extrair_dados_dos_alertas(alertas_volatilidade)
            
            return {
                "categoria": "VOLATILIDADE",
                "timestamp": datetime.utcnow().isoformat(),
                "dados_coletados": dados_extraidos["dados"],
                "alertas_status": dados_extraidos["status"],
                "alertas_detectados": len(alertas_volatilidade),
                "alertas_detalhes": [
                    {
                        "titulo": a.titulo,
                        "mensagem": a.mensagem,
                        "categoria": a.categoria.value,
                        "valor_atual": a.valor_atual,
                        "threshold": a.threshold_configurado,
                        "acao": a.dados_contexto.get("acao_recomendada"),
                        "tipo": a.dados_contexto.get("tipo_volatilidade")
                    } for a in alertas_volatilidade
                ],
                "resumo_categoria": {
                    "total_alertas_possiveis": 5,
                    "alertas_disparados": len(alertas_volatilidade),
                    "urgencia": "ALTA" if any(a.categoria == CategoriaAlerta.CRITICO for a in alertas_volatilidade) else "NORMAL",
                    "proxima_verificacao": "1h"
                },
                "fontes_dados": {
                    "mesmo_codigo_producao": True,
                    "zero_divergencia": True
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
    
    def _extrair_dados_dos_alertas(self, alertas: List[AlertaCreate]) -> dict:
        """Extrai dados dos alertas para debug sem duplicar lógica"""
        dados = {}
        status = {}
        
        for alerta in alertas:
            tipo_vol = alerta.dados_contexto.get("tipo_volatilidade")
            
            if tipo_vol == "compressao_extrema":
                dados["bbw_percentage"] = alerta.valor_atual
                dados["dias_bbw_baixo"] = alerta.dados_contexto.get("dias_comprimido")
                status["bbw_compressao_extrema"] = {
                    "disparado": True,
                    "valor_atual": alerta.valor_atual,
                    "threshold": alerta.threshold_configurado,
                    "acao": alerta.dados_contexto.get("acao_recomendada")
                }
            elif tipo_vol == "volume_spike":
                dados["volume_spike_percent"] = alerta.valor_atual
                status["volume_spike"] = {
                    "disparado": True,
                    "valor_atual": alerta.valor_atual,
                    "threshold": alerta.threshold_configurado,
                    "acao": alerta.dados_contexto.get("acao_recomendada")
                }
            elif tipo_vol == "atr_minimo":
                dados["atr_percent"] = alerta.valor_atual
                status["atr_minimo"] = {
                    "disparado": True,
                    "valor_atual": alerta.valor_atual,
                    "threshold": alerta.threshold_configurado,
                    "acao": alerta.dados_contexto.get("acao_recomendada")
                }
            elif tipo_vol == "oportunidade_realizacao":
                dados["ema144_distance"] = alerta.dados_contexto.get("ema_distance")
                dados["rsi_diario"] = alerta.dados_contexto.get("rsi_diario")
                status["ema_rsi_realizar"] = {
                    "disparado": True,
                    "acao": alerta.dados_contexto.get("acao_recomendada")
                }
        
        # Adicionar status padrão para alertas não disparados
        alertas_nao_disparados = {
            "bbw_compressao_extrema": {"disparado": False, "acao": "Monitorar"},
            "volume_spike": {"disparado": False, "acao": "Normal"},
            "atr_minimo": {"disparado": False, "acao": "Normal"},
            "ema_rsi_realizar": {"disparado": False, "acao": "Hold"},
            "pump_drift": {"disparado": False, "acao": "Aguardar padrão"}
        }
        
        for key, default in alertas_nao_disparados.items():
            if key not in status:
                status[key] = default
        
        return {"dados": dados, "status": status}