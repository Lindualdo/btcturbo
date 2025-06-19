# app/services/v3/dash_main/utils/helpers/data_builder.py

import logging
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)

def build_dashboard_data(dados_mercado: dict, dados_risco: dict, dados_alavancagem: dict, dados_tatica: dict) -> dict:
    """
    Constrói dados V3 formato compatível com JSON esperado
    
    Args:
        dados_mercado: Dados reais Camada 1
        dados_risco: Dados reais Camada 2  
        dados_alavancagem: Dados reais Camada 3
        dados_tatica: Dados reais Camada 4 (tecnicos + estrategia)
    """
    try:
        logger.info("🔧 Construindo dados Dashboard V3...")
        
        # Validar inputs obrigatórios
        if not dados_mercado:
            raise Exception("Dados mercado ausentes")
        if not dados_risco or dados_risco.get("status") != "success":  
            raise Exception("Dados risco inválidos")
        if not dados_alavancagem or dados_alavancagem.get("status") != "success":
            raise Exception("Dados alavancagem inválidos")
        if not dados_tatica or not dados_tatica.get("tecnicos") or not dados_tatica.get("estrategia"):
            raise Exception("Dados tática inválidos")
        
        # Extrair dados reais das 4 camadas
        btc_price = _extract_btc_price(dados_mercado, dados_risco)
        position_usd = _extract_position_value(dados_risco)
        
        # Dados técnicos da Camada 4
        tecnicos = dados_tatica["tecnicos"]
        estrategia = dados_tatica["estrategia"]
        
        # Campos para PostgreSQL
        campos = {
            "btc_price": btc_price,
            "score_mercado": dados_mercado["score_mercado"],
            "score_risco": dados_risco["score"],
            "ciclo_atual": dados_mercado["ciclo"],
            "setup_4h": estrategia.get("setup_4h", "NENHUM"),
            "decisao_final": estrategia.get("decisao", "AGUARDAR"),
            "alavancagem_atual": dados_alavancagem.get("alavancagem_atual", 0),
            "health_factor": dados_risco["health_factor"],
            "ema_distance": tecnicos.get("ema_144_distance", 0),
            "rsi_diario": tecnicos.get("rsi", 50)  # RSI 4H (renomear campo futuro)
        }
        
        # JSON completo formato esperado
        dashboard_json = {
            "header": {
                "btc_price": campos["btc_price"],
                "position_usd": position_usd
            },
            "scores": {
                "ciclo": campos["ciclo_atual"],
                "risco": campos["score_risco"],
                "mercado": campos["score_mercado"],
                "classificacao_risco": dados_risco["classificacao"],
                "classificacao_mercado": dados_mercado["classificacao_mercado"]
            },
            "tecnicos": {
                "rsi": tecnicos.get("rsi", 50),
                "preco_ema144": tecnicos.get("preco_ema144", 0),
                "ema_144_distance": tecnicos.get("ema_144_distance", 0)
            },
            "estrategia": {
                "decisao": estrategia.get("decisao", "AGUARDAR"),
                "setup_4h": estrategia.get("setup_4h", "NENHUM"),
                "urgencia": estrategia.get("urgencia", "baixa"),
                "justificativa": estrategia.get("justificativa", "Dados indisponíveis")
            },
            "alavancagem": {
                "atual": dados_alavancagem.get("alavancagem_atual", 0),
                "status": dados_alavancagem.get("posicao_financeira", {}).get("status_posicao", "indefinido"),
                "permitida": dados_alavancagem.get("alavancagem_permitida", 0),
                "divida_total": dados_alavancagem.get("posicao_financeira", {}).get("divida_total", 0),
                "valor_a_reduzir": dados_alavancagem.get("posicao_financeira", {}).get("valor_a_reduzir", 0),
                "valor_disponivel": dados_alavancagem.get("posicao_financeira", {}).get("valor_disponivel", 0)
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

def _extract_btc_price(dados_mercado: dict, dados_risco: dict) -> float:
    """Extrai preço BTC dos dados disponíveis"""
    try:
        # Prioridade: dados técnicos > mercado > risco
        if "btc_price" in dados_mercado:
            return float(dados_mercado["btc_price"])
        elif "btc_price" in dados_risco:
            return float(dados_risco["btc_price"])
        else:
            # Fallback: buscar via helper
            from app.services.utils.helpers.tradingview.tradingview_helper import fetch_ohlc_data
            from tvDatafeed import Interval
            
            df = fetch_ohlc_data("BTCUSDT", "BINANCE", Interval.in_4_hour, 1)
            return float(df['close'].iloc[-1])
            
    except Exception as e:
        logger.error(f"❌ Erro extrair BTC price: {str(e)}")
        return 100000.0  # Fallback

def _extract_position_value(dados_risco: dict) -> float:
    """Extrai valor posição USD"""
    try:
        # Buscar nos indicadores de risco
        if "position_usd" in dados_risco:
            return float(dados_risco["position_usd"])
        else:
            logger.warning("⚠️ Position USD não encontrado - usando fallback")
            return 100000.0  # Fallback
            
    except Exception as e:
        logger.error(f"❌ Erro extrair position: {str(e)}")
        return 100000.0

def build_response_format(dados_db: dict) -> dict:
    """
    Constrói resposta formato API V3 a partir dos dados do banco
    """
    try:
        # Extrair JSON do campo dashboard_json
        dashboard_json = dados_db.get("dashboard_json")
        
        # Se for string, fazer parse
        if isinstance(dashboard_json, str):
            import json
            dashboard_json = json.loads(dashboard_json)
        
        # Se não tiver JSON válido, construir a partir dos campos
        if not dashboard_json:
            logger.warning("⚠️ JSON vazio - construindo a partir dos campos")
            dashboard_json = _build_from_fields(dados_db)
        
        return {
            "status": "success",
            "data": dashboard_json,
            "metadata": {
                "id": dados_db.get("id", 0),
                "timestamp": dados_db["created_at"].isoformat() if dados_db.get("created_at") else datetime.utcnow().isoformat(),
                "age_minutes": _calculate_age_minutes(dados_db.get("created_at")) if dados_db.get("created_at") else 0,
                "versao": "v3_4_camadas"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro build response: {str(e)}")
        return {
            "status": "error",
            "erro": str(e),
            "versao": "v3_4_camadas"
        }

def _build_from_fields(dados_db: dict) -> dict:
    """Constrói JSON a partir dos campos do banco em caso de falha"""
    try:
        return {
            "header": {
                "btc_price": dados_db.get("btc_price", 0),
                "position_usd": 100000.0  # Fallback
            },
            "scores": {
                "ciclo": dados_db.get("ciclo_atual", "INDEFINIDO"),
                "risco": dados_db.get("score_risco", 0),
                "mercado": dados_db.get("score_mercado", 0),
                "classificacao_risco": "indefinido",
                "classificacao_mercado": "indefinido"
            },
            "tecnicos": {
                "rsi": dados_db.get("rsi_diario", 50),
                "preco_ema144": 0,
                "ema_144_distance": dados_db.get("ema_distance", 0)
            },
            "estrategia": {
                "decisao": dados_db.get("decisao_final", "INDEFINIDO"),
                "setup_4h": dados_db.get("setup_4h", "INDEFINIDO"),
                "urgencia": "baixa",
                "justificativa": "Dados reconstruídos"
            },
            "alavancagem": {
                "atual": dados_db.get("alavancagem_atual", 0),
                "status": "indefinido",
                "permitida": 0,
                "divida_total": 0,
                "valor_a_reduzir": 0,
                "valor_disponivel": 0
            },
            "indicadores": {
                "mvrv": 0,
                "nupl": 0,
                "health_factor": dados_db.get("health_factor", 0),
                "dist_liquidacao": 0
            }
        }
    except Exception as e:
        logger.error(f"❌ Erro construir fallback: {str(e)}")
        return {}

def _calculate_age_minutes(created_at: datetime) -> float:
    """Calcula idade em minutos do registro"""
    try:
        now = datetime.utcnow()
        delta = now - created_at
        return round(delta.total_seconds() / 60, 5)
    except:
        return 0.0