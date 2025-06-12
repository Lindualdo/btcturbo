# app/services/alertas/detectores/taticos_detector.py

import logging
from typing import List, Optional
from datetime import datetime
from ..models import AlertaCreate, TipoAlerta, CategoriaAlerta
from ...utils.helpers.analise.ema144_live_helper import obter_ema144_distance_atualizada
from ...utils.helpers.tradingview.rsi_helper import obter_rsi_diario
from ...analises.analise_mercado import calcular_analise_mercado
from ...utils.helpers.postgres import get_dados_risco
from ...utils.helpers.tradingview.tradingview_helper import fetch_ohlc_data
from tvDatafeed import Interval

logger = logging.getLogger(__name__)

class TaticosDetector:
    """
    Detecta alertas TÁTICOS - Entradas/saídas específicas
    
    Alertas (6):
    1. EMA144 < -8% + RSI < 40 = Compra (desconto + oversold)
    2. Score mercado > 70 + leverage < max*0.7 = Aumentar posição
    3. EMA144 > 15% + 5 dias green = Realização parcial
    4. Funding negativo + preço estável = Oportunidade
    5. DCA opportunity = Acumulação gradual
    6. Breakout confirmation = Entrada após confirmação
    """
    
    def verificar_alertas(self) -> List[AlertaCreate]:
        """Verifica todos os alertas táticos"""
        alertas = []
        
        try:
            logger.info("🎯 Verificando alertas TÁTICOS...")
            
            # 1. INFORMATIVO: EMA144 < -8% + RSI < 40 (compra)
            compra_desconto = self._check_compra_desconto()
            if compra_desconto:
                alertas.append(compra_desconto)
            
            # 2. INFORMATIVO: Score mercado > 70 + leverage baixo (aumentar)
            aumentar_posicao = self._check_aumentar_posicao()
            if aumentar_posicao:
                alertas.append(aumentar_posicao)
            
            # 3. INFORMATIVO: EMA144 > 15% + 5 dias green (parcial)
            realizacao_parcial = self._check_realizacao_parcial()
            if realizacao_parcial:
                alertas.append(realizacao_parcial)
            
            # 4. INFORMATIVO: Funding negativo + preço estável
            funding_oportunidade = self._check_funding_oportunidade()
            if funding_oportunidade:
                alertas.append(funding_oportunidade)
            
            # 5. INFORMATIVO: DCA opportunity
            dca_opportunity = self._check_dca_opportunity()
            if dca_opportunity:
                alertas.append(dca_opportunity)
            
            # 6. INFORMATIVO: Breakout confirmation
            breakout_confirmation = self._check_breakout_confirmation()
            if breakout_confirmation:
                alertas.append(breakout_confirmation)
            
            logger.info(f"🎯 Táticos: {len(alertas)} alertas detectados")
            return alertas
            
        except Exception as e:
            logger.error(f"❌ Erro detector táticos: {str(e)}")
            return []
    
    def _check_compra_desconto(self) -> Optional[AlertaCreate]:
        """1. EMA144 < -8% + RSI < 40 = Compra (desconto + oversold)"""
        try:
            ema_distance = obter_ema144_distance_atualizada()
            rsi_diario = obter_rsi_diario()
            
            if ema_distance < -8 and rsi_diario < 40:
                return AlertaCreate(
                    tipo=TipoAlerta.TATICO,
                    categoria=CategoriaAlerta.INFORMATIVO,
                    prioridade=2,
                    titulo="🛒 COMPRA: Desconto + Oversold",
                    mensagem=f"EMA144 {ema_distance:+.1f}% + RSI {rsi_diario:.0f} - Oportunidade compra",
                    threshold_configurado=-8.0,
                    valor_atual=ema_distance,
                    dados_contexto={
                        "ema_distance": ema_distance,
                        "rsi_diario": rsi_diario,
                        "acao_recomendada": "Adicionar 35% à posição",
                        "tipo_tatico": "compra_desconto_oversold",
                        "thresholds": {"ema": -8.0, "rsi": 40.0}
                    },
                    cooldown_minutos=120
                )
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro check compra desconto: {str(e)}")
            return None
    
    def _check_aumentar_posicao(self) -> Optional[AlertaCreate]:
        """2. Score mercado > 70 + leverage < max*0.7 = Aumentar posição"""
        try:
            analise_mercado = calcular_analise_mercado()
            dados_risco = get_dados_risco()
            
            if analise_mercado.get("status") != "success" or not dados_risco:
                return None
            
            score_mercado = analise_mercado.get("score_consolidado", 0)
            alavancagem_atual = self._extract_leverage_value(dados_risco.get("alavancagem"))
            
            # Assumir max alavancagem de 2.0x (pode ser refinado)
            max_leverage = 2.0
            threshold_leverage = max_leverage * 0.7
            
            if score_mercado > 70 and alavancagem_atual and alavancagem_atual < threshold_leverage:
                espaco_disponivel = threshold_leverage - alavancagem_atual
                
                return AlertaCreate(
                    tipo=TipoAlerta.TATICO,
                    categoria=CategoriaAlerta.INFORMATIVO,
                    prioridade=2,
                    titulo="🛒 AUMENTAR: Espaço para Leverage",
                    mensagem=f"Score {score_mercado:.1f} + Leverage {alavancagem_atual:.1f}x < {threshold_leverage:.1f}x",
                    threshold_configurado=70.0,
                    valor_atual=score_mercado,
                    dados_contexto={
                        "score_mercado": score_mercado,
                        "alavancagem_atual": alavancagem_atual,
                        "max_permitido": threshold_leverage,
                        "espaco_disponivel": espaco_disponivel,
                        "acao_recomendada": f"Pode aumentar até {espaco_disponivel:.1f}x",
                        "tipo_tatico": "aumentar_leverage_seguro"
                    },
                    cooldown_minutos=180
                )
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro check aumentar posição: {str(e)}")
            return None
    
    def _check_realizacao_parcial(self) -> Optional[AlertaCreate]:
        """3. EMA144 > 15% + 5 dias green = Realização parcial"""
        try:
            ema_distance = obter_ema144_distance_atualizada()
            
            if ema_distance <= 15:
                return None
            
            # Verificar dias consecutivos green
            df = fetch_ohlc_data(n_bars=7)
            dias_green = self._count_consecutive_green_days(df)
            
            if dias_green >= 5:
                return AlertaCreate(
                    tipo=TipoAlerta.TATICO,
                    categoria=CategoriaAlerta.INFORMATIVO,
                    prioridade=2,
                    titulo="💰 PARCIAL: Rally Estendido",
                    mensagem=f"EMA144 +{ema_distance:.1f}% + {dias_green} dias green - Realizar 25%",
                    threshold_configurado=15.0,
                    valor_atual=ema_distance,
                    dados_contexto={
                        "ema_distance": ema_distance,
                        "dias_green": dias_green,
                        "acao_recomendada": "Realizar 25% da posição",
                        "tipo_tatico": "realizacao_rally_estendido"
                    },
                    cooldown_minutos=240
                )
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro check realização parcial: {str(e)}")
            return None
    
    def _check_funding_oportunidade(self) -> Optional[AlertaCreate]:
        """4. Funding negativo + preço estável = Oportunidade"""
        try:
            # Mock funding rate - seria integrado com API real
            funding_rate = self._get_funding_rate_mock()
            
            if funding_rate >= 0:
                return None
            
            # Verificar se preço está estável (variação < 2% em 24h)
            df = fetch_ohlc_data(n_bars=2)
            if len(df) < 2:
                return None
            
            variacao_24h = ((df['close'].iloc[-1] / df['close'].iloc[-2]) - 1) * 100
            
            if funding_rate < 0 and abs(variacao_24h) < 2:
                return AlertaCreate(
                    tipo=TipoAlerta.TATICO,
                    categoria=CategoriaAlerta.INFORMATIVO,
                    prioridade=2,
                    titulo="🔄 OPORTUNIDADE: Funding Negativo",
                    mensagem=f"Funding {funding_rate:.3f}% + Preço estável - Ser pago para hold",
                    threshold_configurado=0.0,
                    valor_atual=funding_rate,
                    dados_contexto={
                        "funding_rate": funding_rate,
                        "variacao_24h": variacao_24h,
                        "acao_recomendada": "Manter posição - ser pago funding",
                        "tipo_tatico": "funding_negativo_estavel"
                    },
                    cooldown_minutos=480
                )
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro check funding: {str(e)}")
            return None
    
    def _check_dca_opportunity(self) -> Optional[AlertaCreate]:
        """5. DCA opportunity = Acumulação gradual"""
        try:
            ema_distance = obter_ema144_distance_atualizada()
            rsi_diario = obter_rsi_diario()
            
            # DCA em correções moderadas
            if -15 < ema_distance < -5 and 35 < rsi_diario < 55:
                return AlertaCreate(
                    tipo=TipoAlerta.TATICO,
                    categoria=CategoriaAlerta.INFORMATIVO,
                    prioridade=2,
                    titulo="💎 DCA: Acumulação Gradual",
                    mensagem=f"EMA144 {ema_distance:+.1f}% + RSI {rsi_diario:.0f} - Zona DCA",
                    threshold_configurado=-5.0,
                    valor_atual=ema_distance,
                    dados_contexto={
                        "ema_distance": ema_distance,
                        "rsi_diario": rsi_diario,
                        "acao_recomendada": "DCA pequeno em 3 dias",
                        "tipo_tatico": "dca_correcao_moderada",
                        "zona": "correção_saudável"
                    },
                    cooldown_minutos=360
                )
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro check DCA: {str(e)}")
            return None
    
    def _check_breakout_confirmation(self) -> Optional[AlertaCreate]:
        """6. Breakout confirmation = Entrada após confirmação"""
        try:
            df = fetch_ohlc_data(n_bars=5)
            
            # Verificar breakout com volume
            if 'volume' not in df.columns or df['volume'].isna().all():
                return None
            
            # Verificar se preço quebrou resistência com volume
            preco_atual = float(df['close'].iloc[-1])
            max_3d = float(df['close'].tail(4).max())  # Máxima dos últimos 3 dias (excluindo hoje)
            volume_atual = float(df['volume'].iloc[-1])
            volume_media = float(df['volume'].tail(4).mean())
            
            # Breakout: preço > máxima + volume > 150% da média
            if preco_atual > max_3d and volume_atual > volume_media * 1.5:
                breakout_percent = ((preco_atual / max_3d) - 1) * 100
                volume_spike = ((volume_atual / volume_media) - 1) * 100
                
                return AlertaCreate(
                    tipo=TipoAlerta.TATICO,
                    categoria=CategoriaAlerta.INFORMATIVO,
                    prioridade=2,
                    titulo="🚀 BREAKOUT: Confirmação com Volume",
                    mensagem=f"Breakout +{breakout_percent:.1f}% + Volume +{volume_spike:.0f}%",
                    threshold_configurado=0.0,
                    valor_atual=breakout_percent,
                    dados_contexto={
                        "breakout_percent": breakout_percent,
                        "volume_spike": volume_spike,
                        "resistencia_quebrada": max_3d,
                        "acao_recomendada": "Entrada em breakout confirmado",
                        "tipo_tatico": "breakout_volume_confirmation"
                    },
                    cooldown_minutos=120
                )
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro check breakout: {str(e)}")
            return None
    
    def _extract_leverage_value(self, leverage_raw) -> Optional[float]:
        """Extrai valor numérico da alavancagem"""
        if not leverage_raw:
            return None
        
        try:
            if isinstance(leverage_raw, dict):
                return float(leverage_raw.get("valor_numerico", 0))
            return float(leverage_raw)
        except:
            return None
    
    def _count_consecutive_green_days(self, df) -> int:
        """Conta dias consecutivos de alta"""
        try:
            count = 0
            for i in range(len(df) - 1, 0, -1):
                if df['close'].iloc[i] > df['close'].iloc[i-1]:
                    count += 1
                else:
                    break
            return count
        except:
            return 0
    
    def _get_funding_rate_mock(self) -> float:
        """Mock funding rate - substituir por API real"""
        # Mock: funding rate entre -0.05% e +0.05%
        import random
        return round(random.uniform(-0.05, 0.05), 4)
    
    def get_debug_info(self) -> dict:
        """Debug específico para alertas táticos"""
        try:
            logger.info("🔍 Debug categoria TÁTICOS...")
            
            # Testar cada alerta
            alertas_checks = [
                ("compra_desconto", self._check_compra_desconto()),
                ("aumentar_posicao", self._check_aumentar_posicao()),
                ("realizacao_parcial", self._check_realizacao_parcial()),
                ("funding_oportunidade", self._check_funding_oportunidade()),
                ("dca_opportunity", self._check_dca_opportunity()),
                ("breakout_confirmation", self._check_breakout_confirmation())
            ]
            
            # Coletar dados atuais
            dados_coletados = {}
            alertas_status = {}
            
            try:
                dados_coletados["ema144_distance"] = obter_ema144_distance_atualizada()
                dados_coletados["rsi_diario"] = obter_rsi_diario()
            except:
                dados_coletados["ema144_distance"] = None
                dados_coletados["rsi_diario"] = None
            
            try:
                analise_mercado = calcular_analise_mercado()
                dados_coletados["score_mercado"] = analise_mercado.get("score_consolidado") if analise_mercado.get("status") == "success" else None
            except:
                dados_coletados["score_mercado"] = None
            
            try:
                dados_risco = get_dados_risco()
                dados_coletados["alavancagem_atual"] = self._extract_leverage_value(dados_risco.get("alavancagem")) if dados_risco else None
            except:
                dados_coletados["alavancagem_atual"] = None
            
            # Status de cada alerta
            for nome, check_result in alertas_checks:
                alertas_status[nome] = {
                    "disparado": check_result is not None,
                    "titulo": check_result.titulo if check_result else "Sem alerta",
                    "acao": check_result.dados_contexto.get("acao_recomendada") if check_result else "Aguardar condições"
                }
            
            alertas_detectados = self.verificar_alertas()
            
            return {
                "categoria": "TÁTICOS",
                "timestamp": datetime.utcnow().isoformat(),
                "finalidade": "Entradas/saídas específicas baseadas em confluências",
                "dados_coletados": dados_coletados,
                "alertas_status": alertas_status,
                "alertas_detectados": len(alertas_detectados),
                "resumo_categoria": {
                    "total_alertas_possiveis": 6,
                    "alertas_disparados": len(alertas_detectados),
                    "funcao": "Timing específico operações",
                    "urgencia": "BAIXA"  # Sempre informativo
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro debug táticos: {str(e)}")
            return {
                "categoria": "TÁTICOS",
                "timestamp": datetime.utcnow().isoformat(),
                "erro": str(e),
                "status": "error"
            }