# app/services/alertas/processamento/filtros.py

import logging
from typing import List
from datetime import datetime, timedelta
from ..models import AlertaCreate

logger = logging.getLogger(__name__)

class FiltrosAlertas:
    """
    Aplica filtros anti-spam e inteligência aos alertas
    """
    
    def aplicar_filtros(self, alertas: List[AlertaCreate]) -> List[AlertaCreate]:
        """Aplica todos os filtros aos alertas detectados"""
        try:
            if not alertas:
                return []
            
            # 1. Remover duplicatas exatas
            alertas_unicos = self._remover_duplicatas(alertas)
            
            # 2. Aplicar cooldown por tipo
            alertas_filtrados = self._aplicar_cooldown(alertas_unicos)
            
            # 3. Priorizar críticos
            alertas_priorizados = self._priorizar_criticos(alertas_filtrados)
            
            logger.info(f"🔍 Filtros: {len(alertas)} → {len(alertas_priorizados)} alertas")
            return alertas_priorizados
            
        except Exception as e:
            logger.error(f"❌ Erro aplicando filtros: {str(e)}")
            return alertas
    
    def _remover_duplicatas(self, alertas: List[AlertaCreate]) -> List[AlertaCreate]:
        """Remove alertas duplicados baseado em título"""
        seen_titles = set()
        alertas_unicos = []
        
        for alerta in alertas:
            if alerta.titulo not in seen_titles:
                seen_titles.add(alerta.titulo)
                alertas_unicos.append(alerta)
            else:
                logger.debug(f"⏭️ Removendo duplicata: {alerta.titulo}")
        
        return alertas_unicos
    
    def _aplicar_cooldown(self, alertas: List[AlertaCreate]) -> List[AlertaCreate]:
        """Aplica cooldown baseado no tipo de alerta"""
        # Por enquanto, deixa passar todos
        # O cooldown real é verificado no PostgreSQL
        return alertas
    
    def _priorizar_criticos(self, alertas: List[AlertaCreate]) -> List[AlertaCreate]:
        """Ordena por prioridade (0 = mais crítico)"""
        return sorted(alertas, key=lambda a: (a.prioridade, a.timestamp if hasattr(a, 'timestamp') else datetime.utcnow()))

# app/services/alertas/processamento/formatter.py

import logging
from datetime import datetime
from typing import Dict, Any
from ..models import AlertaResponse, TipoAlerta, CategoriaAlerta

logger = logging.getLogger(__name__)

class AlertaFormatter:
    """
    Formata alertas para exibição no frontend
    """
    
    def formatar_alerta(self, alerta_raw: Dict) -> AlertaResponse:
        """Converte dados brutos do PostgreSQL em AlertaResponse"""
        try:
            # Campos básicos
            alerta = AlertaResponse(
                id=alerta_raw["id"],
                tipo=TipoAlerta(alerta_raw["tipo"]),
                categoria=CategoriaAlerta(alerta_raw["categoria"]),
                prioridade=alerta_raw["prioridade"],
                titulo=alerta_raw["titulo"],
                mensagem=alerta_raw["mensagem"],
                threshold_configurado=alerta_raw.get("threshold_configurado"),
                valor_atual=alerta_raw.get("valor_atual"),
                dados_contexto=alerta_raw.get("dados_contexto", {}),
                ativo=alerta_raw["ativo"],
                resolvido=alerta_raw["resolvido"],
                resolvido_em=alerta_raw.get("resolvido_em"),
                timestamp=alerta_raw["timestamp"]
            )
            
            # Campos computados
            alerta.tempo_ativo = self._calcular_tempo_ativo(alerta.timestamp)
            alerta.acao_sugerida = self._extrair_acao_sugerida(alerta.dados_contexto)
            alerta.icone = self._get_icone_por_categoria(alerta.categoria)
            alerta.cor = self._get_cor_por_categoria(alerta.categoria)
            
            return alerta
            
        except Exception as e:
            logger.error(f"❌ Erro formatando alerta: {str(e)}")
            raise
    
    def _calcular_tempo_ativo(self, timestamp: datetime) -> str:
        """Calcula há quanto tempo o alerta está ativo"""
        try:
            delta = datetime.utcnow() - timestamp
            
            if delta.total_seconds() < 3600:  # < 1h
                minutos = int(delta.total_seconds() / 60)
                return f"{minutos}min"
            elif delta.total_seconds() < 86400:  # < 1 dia
                horas = int(delta.total_seconds() / 3600)
                return f"{horas}h"
            else:
                dias = delta.days
                return f"{dias}d"
                
        except Exception as e:
            logger.error(f"❌ Erro calculando tempo: {str(e)}")
            return "?"
    
    def _extrair_acao_sugerida(self, dados_contexto: Dict) -> str:
        """Extrai ação sugerida do contexto"""
        return dados_contexto.get("acao_recomendada", "Verificar situação")
    
    def _get_icone_por_categoria(self, categoria: CategoriaAlerta) -> str:
        """Retorna ícone baseado na categoria"""
        icones = {
            CategoriaAlerta.CRITICO: "🚨",
            CategoriaAlerta.URGENTE: "⚠️",
            CategoriaAlerta.INFORMATIVO: "ℹ️"
        }
        return icones.get(categoria, "📊")
    
    def _get_cor_por_categoria(self, categoria: CategoriaAlerta) -> str:
        """Retorna cor baseada na categoria"""
        cores = {
            CategoriaAlerta.CRITICO: "red",
            CategoriaAlerta.URGENTE: "orange", 
            CategoriaAlerta.INFORMATIVO: "blue"
        }
        return cores.get(categoria, "gray")
    
    def get_acao_sugerida(self, alerta_raw: Dict) -> str:
        """Extrai ação sugerida para próxima ação do widget"""
        try:
            dados_contexto = alerta_raw.get("dados_contexto", {})
            if isinstance(dados_contexto, str):
                import json
                dados_contexto = json.loads(dados_contexto)
            
            return dados_contexto.get("acao_recomendada", "Verificar alertas críticos")
            
        except Exception as e:
            logger.error(f"❌ Erro extraindo ação: {str(e)}")
            return "Verificar sistema"