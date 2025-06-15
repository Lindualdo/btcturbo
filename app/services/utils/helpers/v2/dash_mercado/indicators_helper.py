# app/services/utils/helpers/v2/dash_mercado/indicators_helper.py

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

def _format_ciclo_with_scores() -> dict:
    """Formata indicadores CICLO com scores individuais"""
    try:
        from app.services.indicadores import ciclos as indicadores_ciclos
        from app.services.scores.ciclos import (
            calcular_mvrv_score, calcular_nupl_score, 
            calcular_realized_score, calcular_puell_score
        )
        
        dados = indicadores_ciclos.obter_indicadores()
        
        if dados.get("status") == "success":
            indicadores = dados["indicadores"]
            
            # Calcular scores individuais
            mvrv_score, mvrv_class = calcular_mvrv_score(indicadores["MVRV_Z"]["valor"])
            nupl_score, nupl_class = calcular_nupl_score(indicadores["NUPL"]["valor"])
            realized_score, realized_class = calcular_realized_score(indicadores["Realized_Ratio"]["valor"])
            puell_score, puell_class = calcular_puell_score(indicadores["Puell_Multiple"]["valor"])
            
            return {
                "mvrv": {
                    "valor": indicadores["MVRV_Z"]["valor"],
                    "score": mvrv_score
                },
                "nupl": {
                    "valor": indicadores["NUPL"]["valor"],
                    "score": nupl_score
                },
                "realized_price_ratio": {
                    "valor": indicadores["Realized_Ratio"]["valor"],
                    "score": realized_score
                },
                "puell_multiple": {
                    "valor": indicadores["Puell_Multiple"]["valor"],
                    "score": puell_score
                }
            }
        else:
            return {}
            
    except Exception as e:
        logger.error(f"❌ Erro _format_ciclo_with_scores: {str(e)}")
        return {}

def _format_momentum_with_scores() -> dict:
    """Formata indicadores MOMENTUM com scores individuais"""
    try:
        from app.services.indicadores import momentum as indicadores_momentum
        from app.services.scores.momentum import (
            calcular_rsi_score, calcular_funding_score,
            calcular_sopr_score, calcular_ls_ratio_score
        )
        
        dados = indicadores_momentum.obter_indicadores()
        
        if dados.get("status") == "success":
            indicadores = dados["indicadores"]
            
            # Calcular scores individuais
            rsi_score, rsi_class = calcular_rsi_score(indicadores["RSI_Semanal"]["valor"])
            funding_score, funding_class = calcular_funding_score(indicadores["Funding_Rates"]["valor"])
            sopr_score, sopr_class = calcular_sopr_score(indicadores["SOPR"]["valor"])
            ls_score, ls_class = calcular_ls_ratio_score(indicadores["Long_Short_Ratio"]["valor"])
            
            return {
                "rsi_semanal": {
                    "valor": indicadores["RSI_Semanal"]["valor"],
                    "score": rsi_score
                },
                "funding_rate": {
                    "valor": indicadores["Funding_Rates"]["valor"],
                    "score": funding_score
                },
                "sopr": {
                    "valor": indicadores["SOPR"]["valor"],
                    "score": sopr_score
                },
                "long_short_ratio": {
                    "valor": indicadores["Long_Short_Ratio"]["valor"],
                    "score": ls_score
                }
            }
        else:
            return {}
            
    except Exception as e:
        logger.error(f"❌ Erro _format_momentum_with_scores: {str(e)}")
        return {}

def _format_tecnico_with_scores() -> dict:
    """Formata indicadores TÉCNICO com scores e descrições"""
    try:
        from app.services.scores import tecnico as score_tecnico
        
        # Obter score técnico completo
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
        logger.error(f"❌ Erro _format_tecnico_with_scores: {str(e)}")
        return {
            "semanal": {"score": 0, "descricao": "N/A"},
            "diario": {"score": 0, "descricao": "N/A"}
        }