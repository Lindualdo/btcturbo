# app/services/alertas/detectores/mercado_detector.py

import logging
from typing import List
from ..models import AlertaCreate, TipoAlerta, CategoriaAlerta

logger = logging.getLogger(__name__)

class MercadoDetector:
    """
    Detecta alertas de mercado (MVRV extremos, mudanças regime)
    TODO: Implementar após MVP básico
    """
    
    def verificar_alertas(self) -> List[AlertaCreate]:
        """Mock - implementar depois"""
        # TODO: Implementar:
        # - MVRV > 5 (topo zone)
        # - Score mercado mudou 20+ pontos
        # - RSI semanal > 75 + RSI diário > 75
        logger.debug("📊 MercadoDetector: Mock ativo")
        return []

# app/services/alertas/detectores/tatico_detector.py

import logging
from typing import List
from ..models import AlertaCreate, TipoAlerta, CategoriaAlerta

logger = logging.getLogger(__name__)

class TaticoDetector:
    """
    Detecta alertas táticos (entradas/saídas específicas)
    TODO: Implementar após MVP básico
    """
    
    def verificar_alertas(self) -> List[AlertaCreate]:
        """Mock - implementar depois"""
        # TODO: Implementar:
        # - EMA144 < -8% + RSI < 40 (compra)
        # - Score mercado > 70 + leverage < max * 0.7 (aumentar)
        # - Pump & Drift detectado
        logger.debug("🎯 TaticoDetector: Mock ativo")
        return []

# app/services/alertas/detectores/onchain_detector.py

import logging
from typing import List
from ..models import AlertaCreate, TipoAlerta, CategoriaAlerta

logger = logging.getLogger(__name__)

class OnchainDetector:
    """
    Detecta alertas on-chain (baleias, divergências)
    TODO: Implementar após MVP básico
    """
    
    def verificar_alertas(self) -> List[AlertaCreate]:
        """Mock - implementar depois"""
        # TODO: Implementar:
        # - Exchange whale ratio > 85%
        # - Dormancy flow > 500k
        # - Divergências preço vs netflow
        logger.debug("🐋 OnchainDetector: Mock ativo")
        return []