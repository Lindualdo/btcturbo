# app/services/indicadores/tecnico_v3.py - VERSÃO SIMPLIFICADA CORRIGIDA

import logging
from app.services.utils.helpers.postgres.indicadores.tecnico_v3_helper import get_dados_tecnico

logger = logging.getLogger(__name__)

def obter_indicadores():
    """Obter indicadores técnicos v3.0 do banco - VERSÃO SIMPLIFICADA"""
    try:
        logger.info("🔍 Obtendo indicadores técnicos v3.0 SIMPLIFICADOS...")
        
        dados_db = get_dados_tecnico()
        
        if not dados_db:
            return {
                "status": "error", 
                "erro": "Nenhum dado técnico v3.0 encontrado",
                "bloco": "tecnico"
            }
        
        # Resposta compatível com formato atual, mas usando APENAS campos básicos gravados
        return {
            "status": "success",
            "bloco": "tecnico_v3", 
            "timestamp": dados_db.get("timestamp"),
            
            # === CAMPO PRINCIPAL ESPERADO PELO SISTEMA ===
            "score_consolidado": dados_db.get("score_final_ponderado"),
            
            # === CAMPOS SECUNDÁRIOS (usando dados básicos) ===
            "score_semanal": {
                "score_total": dados_db.get("score_consolidado_1w")
            },
            "score_diario": {
                "score_total": dados_db.get("score_consolidado_1d")
            },
            
            # === DADOS BRUTOS EMAs (para compatibilidade) ===
            "emas_semanal": {
                "ema_17": dados_db.get("ema_17_1w"),
                "ema_34": dados_db.get("ema_34_1w"),
                "ema_144": dados_db.get("ema_144_1w"),
                "ema_305": dados_db.get("ema_305_1w"),
                "ema_610": dados_db.get("ema_610_1w")
            },
            "emas_diario": {
                "ema_17": dados_db.get("ema_17_1d"),
                "ema_34": dados_db.get("ema_34_1d"),
                "ema_144": dados_db.get("ema_144_1d"),
                "ema_305": dados_db.get("ema_305_1d"),
                "ema_610": dados_db.get("ema_610_1d")
            },
            "btc_price_current": dados_db.get("btc_price_current"),
            
            # === METADADOS ===
            "fonte": dados_db.get("fonte")
        }
        
    except Exception as e:
        logger.error(f"❌ Erro obter indicadores técnicos v3.0: {str(e)}")
        return {
            "status": "error",
            "erro": str(e),
            "bloco": "tecnico"
        }