# app/services/alertas/detectores/urgentes_detector.py

import logging
from typing import List, Optional
from datetime import datetime
from ..models import AlertaCreate, TipoAlerta, CategoriaAlerta
from ...utils.helpers.postgres import get_dados_risco
from ...analises.analise_risco import calcular_analise_risco

logger = logging.getLogger(__name__)

class UrgentesDetector:
    """
    Detecta alertas URGENTES (preventivos antes dos críticos)
    
    FINALIDADE: Aviso preventivo antes dos alertas críticos
    REUTILIZAÇÃO: Mesmas funções do CriticosDetector com thresholds diferentes
    
    Alertas (3):
    1. Health Factor < 1.5 (antes do crítico 1.3)
    2. Distância Liquidação < 30% (antes do crítico 20%)  
    3. Score Risco < 50 (antes do crítico 30)
    """
    
    def verificar_alertas(self) -> List[AlertaCreate]:
        """Verifica todos os alertas urgentes preventivos"""
        alertas = []
        
        try:
            logger.info("🟡 Verificando alertas URGENTES...")
            
            # Buscar dados (REUTILIZANDO funções dos críticos)
            dados_risco = get_dados_risco()
            analise_risco = calcular_analise_risco()
            
            if not dados_risco:
                logger.warning("⚠️ Dados de risco indisponíveis para urgentes")
                return alertas
            
            # 1. URGENTE: Health Factor < 1.5 (preventivo do 1.3 crítico)
            hf_urgente = self._check_health_factor_urgente(dados_risco)
            if hf_urgente:
                alertas.append(hf_urgente)
            
            # 2. URGENTE: Distância Liquidação < 30% (preventivo do 20% crítico)
            dist_urgente = self._check_distancia_liquidacao_urgente(dados_risco)
            if dist_urgente:
                alertas.append(dist_urgente)
            
            # 3. URGENTE: Score Risco < 50 (preventivo do 30 crítico)
            score_urgente = self._check_score_risco_urgente(analise_risco)
            if score_urgente:
                alertas.append(score_urgente)
            
            logger.info(f"🟡 Urgentes: {len(alertas)} alertas detectados")
            return alertas
            
        except Exception as e:
            logger.error(f"❌ Erro detector urgentes: {str(e)}")
            return []
    
    def _check_health_factor_urgente(self, dados_risco) -> Optional[AlertaCreate]:
        """1. Health Factor < 1.5 = Atenção necessária (PREVENTIVO)"""
        try:
            health_factor = float(dados_risco.get("health_factor", 999))
            
            # REUTILIZAÇÃO: Mesma lógica dos críticos, threshold diferente
            if 1.3 <= health_factor < 1.5:  # Entre crítico e urgente
                return AlertaCreate(
                    tipo=TipoAlerta.POSICAO,
                    categoria=CategoriaAlerta.URGENTE,
                    prioridade=1,
                    titulo="⚠️ ATENÇÃO: Health Factor",
                    mensagem=f"Health Factor {health_factor:.2f} - Monitorar de perto",
                    threshold_configurado=1.5,
                    valor_atual=health_factor,
                    dados_contexto={
                        "acao_recomendada": "Preparar redução preventiva",
                        "risco": "Aproximando zona crítica",
                        "timeframe": "1-4 horas",
                        "tipo_urgente": "health_factor_preventivo",
                        "threshold_critico": 1.3  # Referência ao próximo nível
                    },
                    cooldown_minutos=30
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro check HF urgente: {str(e)}")
            return None
    
    def _check_distancia_liquidacao_urgente(self, dados_risco) -> Optional[AlertaCreate]:
        """2. Distância Liquidação < 30% = Margem apertando (PREVENTIVO)"""
        try:
            # REUTILIZAÇÃO: Mesma função de extração dos críticos
            dist_liquidacao = self._extract_distance_value(dados_risco.get("dist_liquidacao"))
            
            if dist_liquidacao and 20 <= dist_liquidacao < 30:  # Entre crítico e urgente
                return AlertaCreate(
                    tipo=TipoAlerta.POSICAO,
                    categoria=CategoriaAlerta.URGENTE,
                    prioridade=1,
                    titulo="⚠️ CUIDADO: Margem",
                    mensagem=f"Liquidação em -{dist_liquidacao:.1f}% - Preparar redução",
                    threshold_configurado=30.0,
                    valor_atual=dist_liquidacao,
                    dados_contexto={
                        "acao_recomendada": "Considerar redução parcial",
                        "risco": "Margem apertando",
                        "timeframe": "1-4 horas",
                        "tipo_urgente": "distancia_liquidacao_preventivo",
                        "threshold_critico": 20.0
                    },
                    cooldown_minutos=30
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro check distância urgente: {str(e)}")
            return None
    
    def _check_score_risco_urgente(self, analise_risco) -> Optional[AlertaCreate]:
        """3. Score Risco < 50 = Posição arriscada (PREVENTIVO)"""
        try:
            if analise_risco.get("status") != "success":
                return None
            
            # REUTILIZAÇÃO: Mesma lógica dos críticos
            score_risco = analise_risco.get("score_consolidado", 100)
            
            if 30 <= score_risco < 50:  # Entre crítico e urgente
                return AlertaCreate(
                    tipo=TipoAlerta.POSICAO,
                    categoria=CategoriaAlerta.URGENTE,
                    prioridade=1,
                    titulo="⚠️ ALERTA: Score Risco",
                    mensagem=f"Score {score_risco:.1f} - Posição ficando arriscada",
                    threshold_configurado=50.0,
                    valor_atual=score_risco,
                    dados_contexto={
                        "acao_recomendada": "Revisar estratégia posição",
                        "risco": "Score deteriorando",
                        "classificacao": analise_risco.get("classificacao", "alerta"),
                        "tipo_urgente": "score_risco_preventivo",
                        "threshold_critico": 30.0
                    },
                    cooldown_minutos=60
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro check score urgente: {str(e)}")
            return None
    
    def _extract_distance_value(self, dist_raw) -> Optional[float]:
        """REUTILIZAÇÃO: Mesma função dos críticos"""
        if not dist_raw:
            return None
        
        try:
            if isinstance(dist_raw, str):
                return float(dist_raw.replace("%", ""))
            return float(dist_raw)
        except:
            return None
    
    def get_debug_info(self) -> dict:
        """Debug específico para alertas urgentes"""
        try:
            logger.info("🔍 Debug categoria URGENTES...")
            
            dados_risco = get_dados_risco()
            analise_risco = calcular_analise_risco()
            
            # Extrair valores usando mesmas funções
            health_factor = float(dados_risco.get("health_factor", 999)) if dados_risco else None
            dist_liquidacao = self._extract_distance_value(dados_risco.get("dist_liquidacao")) if dados_risco else None
            score_risco = analise_risco.get("score_consolidado", 100) if analise_risco.get("status") == "success" else None
            
            # Status de cada alerta urgente
            alertas_status = {
                "health_factor_urgente": {
                    "valor_atual": health_factor,
                    "threshold": 1.5,
                    "threshold_critico": 1.3,
                    "zona": self._get_zona_risco(health_factor, 1.3, 1.5) if health_factor else "unknown",
                    "disparado": 1.3 <= health_factor < 1.5 if health_factor else False,
                    "acao": self._get_acao_hf(health_factor) if health_factor else "Dados indisponíveis"
                },
                "distancia_liquidacao_urgente": {
                    "valor_atual": dist_liquidacao,
                    "threshold": 30.0,
                    "threshold_critico": 20.0,
                    "zona": self._get_zona_risco(dist_liquidacao, 20.0, 30.0) if dist_liquidacao else "unknown",
                    "disparado": 20 <= dist_liquidacao < 30 if dist_liquidacao else False,
                    "acao": self._get_acao_dist(dist_liquidacao) if dist_liquidacao else "Dados indisponíveis"
                },
                "score_risco_urgente": {
                    "valor_atual": score_risco,
                    "threshold": 50.0,
                    "threshold_critico": 30.0,
                    "zona": self._get_zona_risco(score_risco, 30.0, 50.0) if score_risco else "unknown",
                    "disparado": 30 <= score_risco < 50 if score_risco else False,
                    "acao": self._get_acao_score(score_risco) if score_risco else "Dados indisponíveis"
                }
            }
            
            # Verificar alertas em tempo real
            alertas_detectados = self.verificar_alertas()
            
            return {
                "categoria": "URGENTES",
                "timestamp": datetime.utcnow().isoformat(),
                "finalidade": "Alertas preventivos antes dos críticos",
                "dados_coletados": {
                    "health_factor": health_factor,
                    "dist_liquidacao": dist_liquidacao,
                    "score_risco": score_risco
                },
                "alertas_status": alertas_status,
                "alertas_detectados": len(alertas_detectados),
                "resumo_categoria": {
                    "total_alertas_possiveis": 3,
                    "alertas_disparados": len(alertas_detectados),
                    "funcao": "Aviso preventivo",
                    "urgencia": "MEDIA" if len(alertas_detectados) > 0 else "BAIXA"
                },
                "relacao_criticos": {
                    "health_factor": {
                        "urgente": 1.5,
                        "critico": 1.3,
                        "gap": 0.2
                    },
                    "dist_liquidacao": {
                        "urgente": 30.0,
                        "critico": 20.0,
                        "gap": 10.0
                    },
                    "score_risco": {
                        "urgente": 50.0,
                        "critico": 30.0,
                        "gap": 20.0
                    }
                },
                "fontes_dados": {
                    "dados_risco_ok": dados_risco is not None,
                    "analise_risco_ok": analise_risco.get("status") == "success",
                    "reutilizacao_criticos": True
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro debug urgentes: {str(e)}")
            return {
                "categoria": "URGENTES",
                "timestamp": datetime.utcnow().isoformat(),
                "erro": str(e),
                "status": "error"
            }
    
    def _get_zona_risco(self, valor: float, threshold_critico: float, threshold_urgente: float) -> str:
        """Determina zona de risco baseada nos thresholds"""
        if valor < threshold_critico:
            return "CRÍTICA"
        elif valor < threshold_urgente:
            return "URGENTE" 
        else:
            return "SEGURA"
    
    def _get_acao_hf(self, health_factor: float) -> str:
        """Ação recomendada para Health Factor"""
        if health_factor < 1.3:
            return "🚨 CRÍTICO: Reduzir 70% AGORA"
        elif health_factor < 1.5:
            return "⚠️ URGENTE: Preparar redução preventiva"
        elif health_factor < 2.0:
            return "🟡 ATENÇÃO: Monitorar evolução"
        else:
            return "✅ SEGURO: Sem ação necessária"
    
    def _get_acao_dist(self, dist_liquidacao: float) -> str:
        """Ação recomendada para distância liquidação"""
        if dist_liquidacao < 20:
            return "🚨 CRÍTICO: EMERGÊNCIA - Reduzir posição"
        elif dist_liquidacao < 30:
            return "⚠️ URGENTE: Considerar redução parcial"
        elif dist_liquidacao < 40:
            return "🟡 ATENÇÃO: Monitorar margem"
        else:
            return "✅ SEGURO: Margem confortável"
    
    def _get_acao_score(self, score_risco: float) -> str:
        """Ação recomendada para score de risco"""
        if score_risco < 30:
            return "🚨 CRÍTICO: Fechar posição"
        elif score_risco < 50:
            return "⚠️ URGENTE: Revisar estratégia"
        elif score_risco < 70:
            return "🟡 ATENÇÃO: Posição arriscada"
        else:
            return "✅ SEGURO: Risco controlado"