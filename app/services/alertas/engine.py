# app/services/alertas/engine.py - ATUALIZADO COM URGENTES

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from .models import AlertaResponse, AlertaCreate, AlertaResumo, TipoAlerta, CategoriaAlerta
from .detectores.criticos_detector import CriticosDetector
from .detectores.urgentes_detector import UrgentesDetector  # NOVO
from .detectores.volatilidade_detector import VolatilidadeDetector
from .detectores.mercado_detector import MercadoDetector
from .processamento.filtros import FiltrosAlertas
from .processamento.filtros import AlertaFormatter
from ..utils.helpers.postgres.alertas_helper import AlertasPostgresHelper

logger = logging.getLogger(__name__)

class AlertasEngine:
    """
    Motor principal do sistema de alertas - ATUALIZADO
    Agora inclui detector de Urgentes
    """
    
    def __init__(self):
        # Detectores por categoria - ATUALIZADO
        self.detectores = {
            TipoAlerta.POSICAO: CriticosDetector(),         # Críticos (5 alertas)
            "urgentes": UrgentesDetector(),                 # NOVO: Urgentes (3 alertas)
            TipoAlerta.VOLATILIDADE: VolatilidadeDetector(), # Volatilidade (5 alertas)
            TipoAlerta.MERCADO: MercadoDetector()           # Mercado (mock)
        }
        
        self.filtros = FiltrosAlertas()
        self.formatter = AlertaFormatter()
        self.db_helper = AlertasPostgresHelper()
        self.ultima_verificacao = None
    

        """Sugere próxima ação baseada nos alertas críticos/urgentes"""
        try:
            # Priorizar críticos primeiro
            alerta_critico = self.db_helper.get_alerta_mais_critico()
            if alerta_critico:
                return self.formatter.get_acao_sugerida(alerta_critico)
            
            # Se não há críticos, buscar urgentes
            alertas_urgentes = self.db_helper.get_alertas_ativos(categoria="urgente", limit=1)
            if alertas_urgentes:
                return self.formatter.get_acao_sugerida(alertas_urgentes[0])
            
            return None
        except:
            return None