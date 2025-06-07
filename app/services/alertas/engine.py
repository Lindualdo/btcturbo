# app/services/alertas/engine.py

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from .models import AlertaResponse, AlertaCreate, AlertaResumo, TipoAlerta, CategoriaAlerta
from .detectores.criticos_detector import CriticosDetector
from .detectores.volatilidade_detector import VolatilidadeDetector
from .detectores.mercado_detector import MercadoDetector
#from .detectores.tatico_detector import TaticoDetector
#from .detectores.onchain_detector import OnchainDetector
from .processamento.filtros import FiltrosAlertas
from .processamento.filtros import AlertaFormatter
from ..utils.helpers.postgres.alertas_helper import AlertasPostgresHelper

logger = logging.getLogger(__name__)

class AlertasEngine:
    """
    Motor principal do sistema de alertas
    Coordena detecção, filtragem e persistência
    """
    
    def __init__(self):
        # Detectores por categoria - ATUALIZADO
        self.detectores = {
            TipoAlerta.POSICAO: CriticosDetector(),
            TipoAlerta.VOLATILIDADE: VolatilidadeDetector(),  # NOVO
            TipoAlerta.MERCADO: MercadoDetector()
            #TipoAlerta.TATICO: TaticoDetector(),
            #TipoAlerta.ONCHAIN: OnchainDetector()
        }
        
        self.filtros = FiltrosAlertas()
        self.formatter = AlertaFormatter()
        self.db_helper = AlertasPostgresHelper()
        self.ultima_verificacao = None
    
    def verificar_todos_alertas(self) -> Dict[str, Any]:
        """
        FUNÇÃO PRINCIPAL: Verifica todos os tipos de alertas
        """
        try:
            logger.info("🔔 Iniciando verificação completa de alertas...")
            
            alertas_detectados = []
            status_detectores = {}
            
            # Executar cada detector
            for tipo, detector in self.detectores.items():
                try:
                    logger.info(f"🔍 Verificando alertas {tipo.value}...")
                    
                    detectados = detector.verificar_alertas()
                    alertas_detectados.extend(detectados)
                    status_detectores[tipo.value] = {
                        "status": "ok",
                        "alertas_detectados": len(detectados)
                    }
                    
                    logger.info(f"✅ {tipo.value}: {len(detectados)} alertas detectados")
                    
                except Exception as e:
                    logger.error(f"❌ Erro detector {tipo.value}: {str(e)}")
                    status_detectores[tipo.value] = {
                        "status": "error",
                        "erro": str(e)
                    }
            
            # Aplicar filtros (cooldown, anti-spam)
            alertas_filtrados = self.filtros.aplicar_filtros(alertas_detectados)
            
            # Persistir alertas novos
            alertas_salvos = []
            for alerta in alertas_filtrados:
                try:
                    alerta_id = self.db_helper.criar_alerta(alerta)
                    if alerta_id:
                        alertas_salvos.append(alerta_id)
                except Exception as e:
                    logger.error(f"❌ Erro salvando alerta: {str(e)}")
            
            self.ultima_verificacao = datetime.utcnow()
            
            resultado = {
                "timestamp": self.ultima_verificacao.isoformat(),
                "alertas_detectados": len(alertas_detectados),
                "alertas_filtrados": len(alertas_filtrados),
                "alertas_salvos": len(alertas_salvos),
                "status_detectores": status_detectores,
                "resumo": self.get_resumo_alertas(),
                "status": "success"
            }
            
            logger.info(f"✅ Verificação concluída: {len(alertas_salvos)} novos alertas")
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Erro na verificação de alertas: {str(e)}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "status": "error",
                "erro": str(e)
            }
    
    def get_alertas_ativos(self, categoria: Optional[str] = None, 
                          tipo: Optional[str] = None, limit: int = 20) -> List[AlertaResponse]:
        """Busca alertas ativos com filtros"""
        try:
            alertas_raw = self.db_helper.get_alertas_ativos(
                categoria=categoria, tipo=tipo, limit=limit
            )
            
            # Enriquecer com formatação
            alertas_formatados = []
            for alerta_raw in alertas_raw:
                alerta = self.formatter.formatar_alerta(alerta_raw)
                alertas_formatados.append(alerta)
            
            return alertas_formatados
            
        except Exception as e:
            logger.error(f"❌ Erro buscando alertas ativos: {str(e)}")
            return []
    
    def get_resumo_alertas(self) -> AlertaResumo:
        """Widget principal - contadores por categoria"""
        try:
            contadores = self.db_helper.get_contadores_alertas()
            
            return AlertaResumo(
                criticos=contadores.get("critico", 0),
                urgentes=contadores.get("urgente", 0), 
                informativos=contadores.get("informativo", 0),
                volatilidade=contadores.get("volatilidade", 0),
                total_ativos=sum(contadores.values()),
                ultima_verificacao=self.ultima_verificacao or datetime.utcnow(),
                proxima_acao=self._get_proxima_acao_sugerida(),
                por_tipo=self.db_helper.get_contadores_por_tipo()
            )
            
        except Exception as e:
            logger.error(f"❌ Erro no resumo de alertas: {str(e)}")
            return AlertaResumo(
                criticos=0, urgentes=0, informativos=0, volatilidade=0,
                total_ativos=0, ultima_verificacao=datetime.utcnow(),
                proxima_acao=None, por_tipo={}
            )
    
    def get_historico_alertas(self, data_inicio: datetime,
                             incluir_resolvidos: bool = True,
                             tipo: Optional[str] = None) -> List[AlertaResponse]:
        """Timeline histórico"""
        try:
            alertas_raw = self.db_helper.get_historico_alertas(
                data_inicio=data_inicio,
                incluir_resolvidos=incluir_resolvidos,
                tipo=tipo
            )
            
            return [self.formatter.formatar_alerta(a) for a in alertas_raw]
            
        except Exception as e:
            logger.error(f"❌ Erro no histórico: {str(e)}")
            return []
    
    def resolver_alerta(self, alerta_id: int) -> bool:
        """Marca alerta como resolvido"""
        try:
            return self.db_helper.resolver_alerta(alerta_id)
        except Exception as e:
            logger.error(f"❌ Erro resolvendo alerta {alerta_id}: {str(e)}")
            return False
    
    def snooze_alerta(self, alerta_id: int, minutos: int) -> bool:
        """Silencia alerta por X minutos"""
        try:
            return self.db_helper.snooze_alerta(alerta_id, minutos)
        except Exception as e:
            logger.error(f"❌ Erro snooze alerta {alerta_id}: {str(e)}")
            return False
    
    def get_config_alertas(self) -> List[Dict]:
        """Configurações atuais"""
        return self.db_helper.get_config_alertas()
    
    def update_config_alertas(self, configs: List[Dict]) -> bool:
        """Atualiza configurações"""
        return self.db_helper.update_config_alertas(configs)
    
    def get_ultima_verificacao(self) -> Optional[datetime]:
        """Timestamp última verificação"""
        return self.ultima_verificacao
    
    def count_alertas_ativos(self) -> int:
        """Conta alertas ativos"""
        return self.db_helper.count_alertas_ativos()
    
    def check_detectores_status(self) -> Dict[str, str]:
        """Status dos detectores"""
        status = {}
        for tipo, detector in self.detectores.items():
            try:
                # Teste básico: verificar se o detector está funcional
                detector.verificar_alertas()
                status[tipo.value] = "operational"
            except Exception as e:
                status[tipo.value] = f"error: {str(e)[:50]}"
        
        return status
    
    def _get_proxima_acao_sugerida(self) -> Optional[str]:
        """Sugere próxima ação baseada nos alertas críticos"""
        try:
            alerta_critico = self.db_helper.get_alerta_mais_critico()
            if alerta_critico:
                return self.formatter.get_acao_sugerida(alerta_critico)
            return None
        except:
            return None