# source: app/services/dashboards/dash_mercado/indicators_helper.py

import logging

logger = logging.getLogger(__name__)

def get_current_indicators_data() -> dict:
    """
    Obtém dados atuais dos indicadores com scores individuais
    
    Returns:
        dict: {"ciclo": {}, "momentum": {}, "tecnico": {}}
    """
    try:
        logger.info("📊 Coletando dados e scores dos indicadores...")
        
        # Coletar dados formatados com scores
        ciclo_data = _format_ciclo_with_scores()
        momentum_data = _format_momentum_with_scores()
        tecnico_data = _format_tecnico_with_scores()
        
        return {
            "ciclo": ciclo_data,
            "momentum": momentum_data,
            "tecnico": tecnico_data
        }
        
    except Exception as e:
        logger.error(f"❌ Erro get_current_indicators_data: {str(e)}")
        return {
            "ciclo": {},
            "momentum": {},
            "tecnico": {}
        }

def get_current_indicators_data() -> dict:
    """
    Obtém dados dos indicadores do último registro de scores
    (dados que foram usados no cálculo)
    """
    try:
        from app.services.v3.dash_mercado import get_latest_dashboard_scores
        
        ultimo = get_latest_dashboard_scores()
        
        if ultimo:
            return _format_indicators_from_db_record(ultimo)
        else:
            return {"ciclo": {}, "momentum": {}, "tecnico": {}}
        
    except Exception as e:
        logger.error(f"❌ Erro get_current_indicators_data: {str(e)}")
        return {"ciclo": {}, "momentum": {}, "tecnico": {}}

def _format_indicators_from_db_record(record: dict) -> dict:
    """Formata indicadores a partir do registro do banco com scores"""
    try:
        from app.services.scores.ciclos import (
            calcular_mvrv_score, calcular_nupl_score,
            calcular_realized_score, calcular_puell_score
        )
        from app.services.scores.momentum import (
            calcular_rsi_score, calcular_funding_score,
            calcular_sopr_score, calcular_ls_ratio_score
        )
        
        # Calcular scores individuais dos valores salvos
        mvrv_score, _ = calcular_mvrv_score(record.get("mvrv_z_score"))
        nupl_score, _ = calcular_nupl_score(record.get("nupl"))
        realized_score, _ = calcular_realized_score(record.get("realized_ratio"))
        puell_score, _ = calcular_puell_score(record.get("puell_multiple"))
        
        rsi_score, _ = calcular_rsi_score(record.get("rsi_semanal"))
        funding_score, _ = calcular_funding_score(record.get("funding_rates"))
        sopr_score, _ = calcular_sopr_score(record.get("sopr"))
        ls_score, _ = calcular_ls_ratio_score(record.get("long_short_ratio"))
        
        return {
            "ciclo": {
                "mvrv": {
                    "valor": record.get("mvrv_z_score"),
                    "score": mvrv_score
                },
                "nupl": {
                    "valor": record.get("nupl"),
                    "score": nupl_score
                },
                "realized_price_ratio": {
                    "valor": record.get("realized_ratio"),
                    "score": realized_score
                },
                "puell_multiple": {
                    "valor": record.get("puell_multiple"),
                    "score": puell_score
                }
            },
            "momentum": {
                "rsi_semanal": {
                    "valor": record.get("rsi_semanal"),
                    "score": rsi_score
                },
                "funding_rate": {
                    "valor": record.get("funding_rates"),
                    "score": funding_score
                },
                "sopr": {
                    "valor": record.get("sopr"),
                    "score": sopr_score
                },
                "long_short_ratio": {
                    "valor": record.get("long_short_ratio"),
                    "score": ls_score
                }
            },
            "tecnico": _get_tecnico_breakdown()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro _format_indicators_from_db_record: {str(e)}")
        return {"ciclo": {}, "momentum": {}, "tecnico": {}}

def _get_tecnico_breakdown() -> dict:
    """Obtém breakdown do score técnico atual"""
    try:
        from app.services.scores import tecnico as score_tecnico
        
        dados = score_tecnico.calcular_score()
        
        if dados.get("status") == "success":
            detalhes = dados.get("detalhes", {})
            
            return {
                "semanal": {
                    "score": detalhes.get("semanal", {}).get("score_total", 0),
                    "descricao": detalhes.get("semanal", {}).get("classificacao", "N/A")
                },
                "diario": {
                    "score": detalhes.get("diario", {}).get("score_total", 0),
                    "descricao": detalhes.get("diario", {}).get("classificacao", "N/A")
                }
            }
        else:
            return {
                "semanal": {"score": 0, "descricao": "N/A"},
                "diario": {"score": 0, "descricao": "N/A"}
            }
            
    except Exception as e:
        logger.error(f"❌ Erro _get_tecnico_breakdown: {str(e)}")
        return {
            "semanal": {"score": 0, "descricao": "N/A"},
            "diario": {"score": 0, "descricao": "N/A"}
        }