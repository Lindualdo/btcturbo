# app/services/v3/dash_main/utils/helpers/data_builder.py

import logging
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)

def build_dashboard_data(dados_mercado: dict, dados_risco: dict, mock_alavancagem: dict, mock_estrategia: dict) -> dict:
    """
    Constrói dados V3 formato compatível com JSON esperado
    
    Args:
        dados_mercado: Dados reais Camada 1
        dados_risco: Dados reais Camada 2  
        mock_alavancagem: Mock Camada 3 (temporário)
        mock_estrategia: Mock Camada 4 (temporário)
    """
    try:
        logger.info("🔧 Construindo dados Dashboard V3...")
        
        # Campos para PostgreSQL
        campos = {
            "btc_price": mock_alavancagem.get("btc_price", 104350.29),
            "score_mercado": dados_mercado["score_mercado"],
            "score_risco": dados_risco["score"],
            "ciclo_atual": dados_mercado["ciclo"],
            "setup_4h": mock_estrategia.get("setup_4h", "PULLBACK_TENDENCIA"),
            "decisao_final": mock_estrategia.get("decisao", "AJUSTAR_ALAVANCAGEM"),
            "alavancagem_atual": mock_alavancagem.get("alavancagem_atual", 2.04),
            "health_factor": dados_risco["health_factor"],
            "ema_distance": mock_alavancagem.get("ema_distance", -1.29),
            "rsi_diario": mock_alavancagem.get("rsi_diario", 43.8)
        }
        
        # JSON completo formato esperado
        dashboard_json = {
            "header": {
                "btc_price": campos["btc_price"],
                "position_usd": mock_alavancagem.get("position_usd", 124987.126836)
            },
            "scores": {
                "ciclo": campos["ciclo_atual"],
                "risco": campos["score_risco"],
                "mercado": campos["score_mercado"],
                "classificacao_risco": dados_risco["classificacao"],
                "classificacao_mercado": dados_mercado["classificacao_mercado"]
            },
            "tecnicos": {
                "rsi": campos["rsi_diario"],
                "preco_ema144": mock_alavancagem.get("preco_ema144", 106080.29630039757),
                "ema_144_distance": campos["ema_distance"]
            },
            "estrategia": {
                "decisao": campos["decisao_final"],
                "setup_4h": campos["setup_4h"],
                "urgencia": mock_estrategia.get("urgencia", "alta"),
                "justificativa": mock_estrategia.get("justificativa", "Alavancagem no limite: 2.0x >= 2.0x")
            },
            "alavancagem": {
                "atual": campos["alavancagem_atual"],
                "status": mock_alavancagem.get("status_alavancagem", "deve_reduzir"),
                "permitida": mock_alavancagem.get("alavancagem_permitida", 2.0),
                "divida_total": mock_alavancagem.get("divida_total", 63836.377046),
                "valor_a_reduzir": mock_alavancagem.get("valor_a_reduzir", 2685.63),
                "valor_disponivel": mock_alavancagem.get("valor_disponivel", 0.0)
            },
            "indicadores": {
                "mvrv": dados_mercado["indicadores"]["mvrv"],
                "nupl": dados_mercado["indicadores"]["nupl"],
                "health_factor": campos["health_factor"],
                "dist_liquidacao": dados_risco["dist_liquidacao"]
            }
        }
        
        return {
            "campos": campos,
            "json": dashboard_json
        }
        
    except Exception as e:
        logger.error(f"❌ Erro construir dados V3: {str(e)}")
        raise Exception(f"Falha construir dados: {str(e)}")

def build_response_format(dashboard_data: dict, record_id: int, timestamp: datetime) -> dict:
    """
    Constrói resposta final formato esperado
    """
    try:
        age_minutes = (datetime.utcnow() - timestamp).total_seconds() / 60
        
        return {
            "status": "success",
            "data": dashboard_data["json"],
            "metadata": {
                "id": record_id,
                "timestamp": timestamp.isoformat(),
                "age_minutes": round(age_minutes, 5),
                "versao": "v3_4_camadas"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro construir resposta: {str(e)}")
        raise Exception(f"Falha construir resposta: {str(e)}")