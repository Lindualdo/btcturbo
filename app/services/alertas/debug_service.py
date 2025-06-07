# app/services/alertas/debug_service.py

import logging
from typing import Dict, Any
from .detectores.posicao_detector import PosicaoDetector
from datetime import datetime

logger = logging.getLogger(__name__)

class AlertasDebugService:
    """
    Service para debug de alertas por categoria
    Mesma estrutura dos detectores = fidelidade teste X produção
    """
    
    def __init__(self):
        self.posicao_detector = PosicaoDetector()
    
    def debug_criticos(self) -> Dict[str, Any]:
        """Debug completo da categoria CRÍTICOS"""
        try:
            logger.info("🔍 Iniciando debug categoria CRÍTICOS...")
            
            # Usar o mesmo detector que produção
            debug_info = self.posicao_detector.get_debug_info()
            
            # Executar detecção real para comparar
            alertas_detectados = self.posicao_detector.verificar_alertas()
            alertas_criticos = [a for a in alertas_detectados if a.categoria.value == "critico"]
            
            # Consolidar informações
            debug_completo = {
                **debug_info,
                "alertas_detectados": len(alertas_criticos),
                "alertas_detalhes": [
                    {
                        "titulo": a.titulo,
                        "mensagem": a.mensagem,
                        "valor_atual": a.valor_atual,
                        "threshold": a.threshold_configurado,
                        "acao": a.dados_contexto.get("acao_recomendada"),
                        "tipo": a.dados_contexto.get("tipo_critico")
                    } for a in alertas_criticos
                ],
                "resumo_categoria": {
                    "categoria": "CRÍTICOS",
                    "total_alertas_possiveis": 5,
                    "alertas_disparados": len(alertas_criticos),
                    "urgencia": "IMEDIATA" if alertas_criticos else "MONITORAR",
                    "proxima_verificacao": "5min" if alertas_criticos else "15min"
                }
            }
            
            logger.info(f"✅ Debug críticos: {len(alertas_criticos)} alertas ativos")
            return debug_completo
            
        except Exception as e:
            logger.error(f"❌ Erro debug críticos: {str(e)}")
            return {
                "categoria": "CRÍTICOS",
                "timestamp": datetime.utcnow().isoformat(),
                "erro": str(e),
                "status": "error"
            }