# app/services/alertas/detectores/posicao_detector.py

import logging
from typing import List
from ..models import AlertaCreate, AlertaDetectado, TipoAlerta, CategoriaAlerta
from ...utils.helpers.postgres import get_dados_risco
from ...analises.analise_risco import calcular_analise_risco
from typing import List, Optional

logger = logging.getLogger(__name__)

class PosicaoDetector:
    """
    Detecta alertas relacionados à proteção da posição atual
    PRIORIDADE 1: Health Factor e Score Risco críticos
    """
    
    def verificar_alertas(self) -> List[AlertaCreate]:
        """Verifica todos os alertas de posição"""
        alertas = []
        
        try:
            # Buscar dados atuais de risco
            dados_risco = get_dados_risco()
            if not dados_risco:
                logger.warning("⚠️ Dados de risco indisponíveis")
                return alertas
            
            # Analisar scores consolidados  
            analise_risco = calcular_analise_risco()
            
            # 1. CRÍTICO: Health Factor < 1.3
            hf_alert = self._check_health_factor_critico(dados_risco)
            if hf_alert:
                alertas.append(hf_alert)
            
            # 2. CRÍTICO: Score Risco < 30
            score_alert = self._check_score_risco_critico(analise_risco)
            if score_alert:
                alertas.append(score_alert)
            
            # 3. URGENTE: Health Factor < 1.5
            hf_urgente = self._check_health_factor_urgente(dados_risco)
            if hf_urgente:
                alertas.append(hf_urgente)
            
            # 4. URGENTE: Distância liquidação < 30%
            dist_alert = self._check_distancia_liquidacao(dados_risco)
            if dist_alert:
                alertas.append(dist_alert)
            
            logger.info(f"✅ Posição: {len(alertas)} alertas detectados")
            return alertas
            
        except Exception as e:
            logger.error(f"❌ Erro detector posição: {str(e)}")
            return []
    
    def _check_health_factor_critico(self, dados_risco) -> Optional[AlertaCreate]:
        """PRIORITÁRIO: Health Factor < 1.3 = Risco crítico"""
        try:
            health_factor = float(dados_risco.get("health_factor", 999))
            
            if health_factor < 1.3:
                return AlertaCreate(
                    tipo=TipoAlerta.POSICAO,
                    categoria=CategoriaAlerta.CRITICO,
                    prioridade=0,
                    titulo="🚨 HEALTH FACTOR CRÍTICO",
                    mensagem=f"Health Factor {health_factor:.2f} < 1.3 - Reduzir 70% AGORA",
                    threshold_configurado=1.3,
                    valor_atual=health_factor,
                    dados_contexto={
                        "acao_recomendada": "Reduzir 70% da posição imediatamente",
                        "risco": "Liquidação iminente",
                        "timeframe": "Imediato"
                    },
                    cooldown_minutos=5  # Alerta crítico = cooldown menor
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro check HF crítico: {str(e)}")
            return None
    
    def _check_score_risco_critico(self, analise_risco) -> Optional[AlertaCreate]:
        """PRIORITÁRIO: Score Risco < 30 = Fechar posição"""
        try:
            if analise_risco.get("status") != "success":
                return None
            
            score_risco = analise_risco.get("score_consolidado", 100)
            
            if score_risco < 30:
                return AlertaCreate(
                    tipo=TipoAlerta.POSICAO,
                    categoria=CategoriaAlerta.CRITICO,
                    prioridade=0,
                    titulo="🚨 RISCO EXTREMO",
                    mensagem=f"Score Risco {score_risco:.1f} < 30 - Fechar posição",
                    threshold_configurado=30.0,
                    valor_atual=score_risco,
                    dados_contexto={
                        "acao_recomendada": "Fechar posição completamente",
                        "risco": "Perda total possível",
                        "classificacao": analise_risco.get("classificacao", "crítico")
                    },
                    cooldown_minutos=10
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro check score risco: {str(e)}")
            return None
    
    def _check_health_factor_urgente(self, dados_risco) -> Optional[AlertaCreate]:
        """Health Factor < 1.5 = Atenção"""
        try:
            health_factor = float(dados_risco.get("health_factor", 999))
            
            # Só alertar se não já alertou crítico
            if 1.3 <= health_factor < 1.5:
                return AlertaCreate(
                    tipo=TipoAlerta.POSICAO,
                    categoria=CategoriaAlerta.URGENTE,
                    prioridade=1,
                    titulo="⚠️ HEALTH FACTOR BAIXO",
                    mensagem=f"Health Factor {health_factor:.2f} < 1.5 - Monitorar de perto",
                    threshold_configurado=1.5,
                    valor_atual=health_factor,
                    dados_contexto={
                        "acao_recomendada": "Preparar redução se continuar caindo",
                        "risco": "Moderado"
                    },
                    cooldown_minutos=30
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro check HF urgente: {str(e)}")
            return None
    
    def _check_distancia_liquidacao(self, dados_risco) -> Optional[AlertaCreate]:
        """Distância liquidação < 30% = Margem apertando"""
        try:
            # Buscar dist_liquidacao dos dados
            dist_liquidacao = None
            
            # Pode vir como string "25.3%" ou como número
            dist_raw = dados_risco.get("dist_liquidacao")
            if dist_raw:
                if isinstance(dist_raw, str):
                    dist_liquidacao = float(dist_raw.replace("%", ""))
                else:
                    dist_liquidacao = float(dist_raw)
            
            if dist_liquidacao and dist_liquidacao < 30:
                return AlertaCreate(
                    tipo=TipoAlerta.POSICAO,
                    categoria=CategoriaAlerta.URGENTE,
                    prioridade=1,
                    titulo="⚠️ MARGEM APERTANDO",
                    mensagem=f"Distância liquidação {dist_liquidacao:.1f}% < 30% - Preparar redução",
                    threshold_configurado=30.0,
                    valor_atual=dist_liquidacao,
                    dados_contexto={
                        "acao_recomendada": "Reduzir alavancagem preventivamente",
                        "risco": "Margem call próxima"
                    },
                    cooldown_minutos=60
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro check distância liquidação: {str(e)}")
            return None