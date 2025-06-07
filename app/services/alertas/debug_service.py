# app/services/alertas/debug_service.py

import logging
from typing import Dict, Any
from .detectores.criticos_detector import   CriticosDetector
from .detectores.volatilidade_detector import VolatilidadeDetector
from datetime import datetime

logger = logging.getLogger(__name__)

class AlertasDebugService:
    """
    Service para debug de alertas por categoria
    Mesma estrutura dos detectores = fidelidade teste X produção
    """
    
    def __init__(self):
        self.posicao_detector = CriticosDetector()
        self.volatilidade_detector = VolatilidadeDetector()
    
    def debug_criticos(self) -> Dict[str, Any]:
        """Debug completo da categoria CRÍTICOS (Posição)"""
        try:
            logger.info("🔍 Iniciando debug categoria CRÍTICOS...")
            return self.posicao_detector.get_debug_info()
            
        except Exception as e:
            logger.error(f"❌ Erro debug críticos: {str(e)}")
            return self._error_response("CRÍTICOS", str(e))
    
    def debug_volatilidade(self) -> Dict[str, Any]:
        """Debug completo da categoria VOLATILIDADE"""
        try:
            logger.info("🔍 Iniciando debug categoria VOLATILIDADE...")
            return self.volatilidade_detector.get_debug_info()
            
        except Exception as e:
            logger.error(f"❌ Erro debug volatilidade: {str(e)}")
            return self._error_response("VOLATILIDADE", str(e))
    
    def debug_geral(self) -> Dict[str, Any]:
        """Overview todas as categorias implementadas"""
        try:
            logger.info("🔍 Debug geral - todas categorias...")
            
            # Debug de cada categoria
            debug_criticos = self.debug_criticos()
            debug_volatilidade = self.debug_volatilidade()
            
            # Consolidar métricas
            total_alertas = (
                debug_criticos.get("alertas_detectados", 0) +
                debug_volatilidade.get("alertas_detectados", 0)
            )
            
            # Status por categoria
            categorias_status = {
                "criticos": {
                    "implementado": True,
                    "funcionando": debug_criticos.get("status") != "error",
                    "alertas_ativos": debug_criticos.get("alertas_detectados", 0),
                    "urgencia": debug_criticos.get("resumo_categoria", {}).get("urgencia", "NORMAL")
                },
                "volatilidade": {
                    "implementado": True,
                    "funcionando": debug_volatilidade.get("status") != "error",
                    "alertas_ativos": debug_volatilidade.get("alertas_detectados", 0),
                    "urgencia": debug_volatilidade.get("resumo_categoria", {}).get("urgencia", "NORMAL")
                },
                "mercado": {
                    "implementado": False,
                    "status": "TODO - MVRV extremos, mudanças regime"
                },
                "tatico": {
                    "implementado": False,
                    "status": "TODO - Entradas/saídas específicas"
                },
                "onchain": {
                    "implementado": False,
                    "status": "TODO - Baleias, divergências"
                }
            }
            
            return {
                "overview": "Sistema de Alertas - Debug Geral",
                "timestamp": datetime.utcnow().isoformat(),
                "sistema_status": {
                    "categorias_implementadas": 2,
                    "categorias_pendentes": 3,
                    "total_alertas_ativos": total_alertas,
                    "sistema_operacional": True
                },
                "categorias_status": categorias_status,
                "detalhes_por_categoria": {
                    "criticos": debug_criticos,
                    "volatilidade": debug_volatilidade
                },
                "proximos_passos": [
                    "Implementar categoria MERCADO",
                    "Implementar categoria TÁTICO", 
                    "Implementar categoria ONCHAIN"
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Erro debug geral: {str(e)}")
            return self._error_response("GERAL", str(e))
    
    def _error_response(self, categoria: str, erro: str) -> Dict[str, Any]:
        """Resposta padrão para erros"""
        return {
            "categoria": categoria,
            "timestamp": datetime.utcnow().isoformat(),
            "erro": erro,
            "status": "error"
        }