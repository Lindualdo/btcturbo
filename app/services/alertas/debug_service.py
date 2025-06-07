# app/services/alertas/debug_service.py - CORRIGIDO (SEM INVENÇÕES)

import logging
from typing import Dict, Any
from .detectores.criticos_detector import CriticosDetector
from .detectores.urgentes_detector import UrgentesDetector  # NOVO
from .detectores.volatilidade_detector import VolatilidadeDetector
from .detectores.taticos_detector import TaticosDetector
from datetime import datetime

logger = logging.getLogger(__name__)

class AlertasDebugService:
    """
    Service para debug de alertas por categoria - CORRIGIDO
    APENAS o que foi pedido: adicionar UrgentesDetector
    """
    
    def __init__(self):
        self.criticos_detector = CriticosDetector()
        self.urgentes_detector = UrgentesDetector()        # NOVO
        self.volatilidade_detector = VolatilidadeDetector()
        self.taticos_detector = TaticosDetector()
    
    def debug_criticos(self) -> Dict[str, Any]:
        """Debug completo da categoria CRÍTICOS"""
        try:
            logger.info("🔍 Iniciando debug categoria CRÍTICOS...")
            return self.criticos_detector.get_debug_info()
            
        except Exception as e:
            logger.error(f"❌ Erro debug críticos: {str(e)}")
            return self._error_response("CRÍTICOS", str(e))
    
    def debug_urgentes(self) -> Dict[str, Any]:
        """NOVO: Debug completo da categoria URGENTES"""
        try:
            logger.info("🔍 Iniciando debug categoria URGENTES...")
            return self.urgentes_detector.get_debug_info()
            
        except Exception as e:
            logger.error(f"❌ Erro debug urgentes: {str(e)}")
            return self._error_response("URGENTES", str(e))
    
    def debug_volatilidade(self) -> Dict[str, Any]:
        """Debug completo da categoria VOLATILIDADE"""
        try:
            logger.info("🔍 Iniciando debug categoria VOLATILIDADE...")
            return self.volatilidade_detector.get_debug_info()
            
        except Exception as e:
            logger.error(f"❌ Erro debug volatilidade: {str(e)}")
            return self._error_response("VOLATILIDADE", str(e))
    
    def debug_tatico (self) -> Dict[str, Any]:
        """Debug completo da categoria Tatico"""
        try:
            logger.info("🔍 Iniciando debug categoria Tatico...")
            return self.taticos_detector.get_debug_info()
            
        except Exception as e:
            logger.error(f"❌ Erro debug Tatico: {str(e)}")
            return self._error_response("Tatico", str(e))
 
    def _error_response(self, categoria: str, erro: str) -> Dict[str, Any]:
        """Resposta padrão para erros"""
        return {
            "categoria": categoria,
            "timestamp": datetime.utcnow().isoformat(),
            "erro": erro,
            "status": "error"
        }