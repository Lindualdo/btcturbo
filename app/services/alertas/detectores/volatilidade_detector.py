# app/services/alertas/detectores/volatilidade_detector.py

import logging
from typing import List, Optional
from datetime import datetime, timedelta
from ..models import AlertaCreate, TipoAlerta, CategoriaAlerta
from ...utils.helpers.postgres import get_dados_tecnico
from ...utils.helpers.bbw_calculator import obter_bbw_com_score
from ...utils.helpers.analise.ema144_live_helper import obter_ema144_distance_atualizada
from ...utils.helpers.rsi_helper import obter_rsi_diario

logger = logging.getLogger(__name__)

class VolatilidadeDetector:
    """
    Detecta alertas de volatilidade e timing
    PRIORIDADE 1: BBW < 5% por 7+ dias = Explosão iminente
    PRIORIDADE 2: EMA144 > 20% + RSI > 70 = Realizar
    """
    
    def __init__(self):
        self.bbw_history = []  # Cache simples para tracking dias
    
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
        """PRIORITÁRIO: BBW < 5% por 7+ dias = Explosão iminente"""
        try:
            bbw_data = obter_bbw_com_score()
            if bbw_data.get("status") != "success":
                return None
            
            bbw_atual = bbw_data["bbw_percentage"]
            
            # Atualizar histórico BBW (implementação simples)
            self.bbw_history.append({
                "timestamp": datetime.utcnow(),
                "bbw": bbw_atual
            })
            
            # Manter apenas últimos 10 dias
            cutoff = datetime.utcnow() - timedelta(days=10)
            self.bbw_history = [h for h in self.bbw_history if h["timestamp"] > cutoff]
            
            # Contar dias consecutivos com BBW < 5%
            dias_comprimido = 0
            for i in range(len(self.bbw_history) - 1, -1, -1):
                if self.bbw_history[i]["bbw"] < 5.0:
                    dias_comprimido += 1
                else:
                    break
            
            if bbw_atual < 10 and dias_comprimido >= 7: #alterado para teste
                return AlertaCreate(
                    tipo=TipoAlerta.VOLATILIDADE,
                    categoria=CategoriaAlerta.CRITICO,
                    prioridade=0,
                    titulo="🔥 EXPLOSÃO IMINENTE",
                    mensagem=f"BBW {bbw_atual:.1f}% há {dias_comprimido} dias - Breakout iminente",
                    threshold_configurado=5.0,
                    valor_atual=bbw_atual,
                    dados_contexto={
                        "dias_comprimido": dias_comprimido,
                        "acao_recomendada": "Preparar capital para breakout",
                        "historico": "Últimas 5 ocorrências = +/-15% avg",
                        "timeframe": "24-72h"
                    },
                    cooldown_minutos=240  # 4h para não spammar
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro check BBW extremo: {str(e)}")
            return None
    
    def _check_ema_rsi_realizar(self) -> Optional[AlertaCreate]:
        """PRIORITÁRIO: EMA144 > 20% + RSI > 70 = Realizar 40%"""
        try:
            ema_distance = obter_ema144_distance_atualizada()
            rsi_diario = obter_rsi_diario()
            
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
            bbw_data = obter_bbw_com_score()
            if bbw_data.get("status") != "success":
                return None
            
            bbw_atual = bbw_data["bbw_percentage"]
            
            # Se BBW está entre 8-15% e antes estava comprimido
            if 8 <= bbw_atual <= 15:
                # Verificar se teve compressão recente
                compressao_recente = any(
                    h["bbw"] < 6 for h in self.bbw_history[-5:] 
                    if h["timestamp"] > datetime.utcnow() - timedelta(days=3)
                )
                
                if compressao_recente:
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
                        cooldown_minutos=360  # 6h
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro check BBW expandindo: {str(e)}")
            return None