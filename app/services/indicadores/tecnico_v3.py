# app/services/indicadores/tecnico_v3.py

import logging
from app.services.utils.helpers.postgres.indicadores.tecnico_v3_helper import get_dados_tecnico

logger = logging.getLogger(__name__)

def obter_indicadores():
    """Obter indicadores técnicos v3.0 do banco"""
    try:
        dados_db = get_dados_tecnico()
        
        if not dados_db:
            return {"status": "error", "erro": "Nenhum dado v3.0 encontrado"}
        
        return {
            "status": "success",
            "bloco": "tecnico_v3", 
            "timestamp": dados_db.get("timestamp"),
            "score_consolidado": dados_db.get("score_final_ponderado"),
            "score_alinhamento_consolidado": dados_db.get("score_alinhamento_v3_1w"),  # Campo gravado
            "score_expansao_consolidado": dados_db.get("score_expansao_v3_1w"),      # Campo gravado
            "score_semanal": {
                "score_total": dados_db.get("score_consolidado_1w"),
                "score_alinhamento": dados_db.get("score_alinhamento_v3_1w"),
                "score_expansao": dados_db.get("score_expansao_v3_1w")
            },
            "score_diario": {
                "score_total": dados_db.get("score_consolidado_1d"), 
                "score_alinhamento": dados_db.get("score_alinhamento_v3_1d"),
                "score_expansao": dados_db.get("score_expansao_v3_1d")
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro obter indicadores v3.0: {str(e)}")
        return {
            "status": "error",
            "erro": str(e)
        }