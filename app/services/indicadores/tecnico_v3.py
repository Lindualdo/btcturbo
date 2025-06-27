# app/services/indicadores/tecnico_v3.py

import logging
from app.services.utils.helpers.postgres.indicadores.tecnico_v3_helper import get_dados_tecnico

logger = logging.getLogger(__name__)

def obter_indicadores():
    """Obter indicadores técnicos v3.0 do banco"""
    try:
        logger.info("🔍 Buscando indicadores técnico v3.0...")
        
        dados_db = get_dados_tecnico()
        
        if not dados_db:
            return {
                "status": "error",
                "erro": "Nenhum dado v3.0 encontrado"
            }
        
        # Debug: verificar campos disponíveis
        logger.info(f"🔍 Campos disponíveis: {list(dados_db.keys())}")
        
        return {
            "status": "success",
            "bloco": "tecnico_v3", 
            "timestamp": dados_db.get("timestamp"),
            "score_consolidado": round(float( dados_db.get("score_final_ponderado")),1),
            "classificacao_consolidada" : get_ema_status_description(dados_db.get("score_final_ponderado")),
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
def get_ema_status_description(score: float) -> str:
    """Converte score numérico EMAs em descrição"""
    if score >= 8.1:
        return "Tendência Forte"
    elif score >= 6.1:
        return "Correção Saudável"
    elif score >= 4.1:
        return "Neutro/Transição"
    elif score >= 2.1:
        return "Reversão Iminente"
    else:
        return "Bear Confirmado"
