# source: app/services/dashboards/dash_mercado_service.py

import logging
from datetime import datetime
from .dash_mercado.main_functions import save_dashboard_scores, collect_and_calculate_scores, get_latest_dashboard_scores

logger = logging.getLogger(__name__)

def processar_dash_mercado() -> dict:
    """
    Calcula dashboard mercado com scores consolidados
    
    Fluxo:
    1. Coleta dados dos 3 blocos
    2. Calcula scores individuais  
    3. Calcula score consolidado
    4. Grava no banco
    """
    try:

        logger.info("🔄 Coletando e calculando scores...")
        
        # 1. Coletar dados e calcular scores
        scores_data = collect_and_calculate_scores()
        
        if scores_data.get("status") != "success":
            return {
                "status": "error",
                "erro": scores_data.get("erro", "Erro ao calcular scores"),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # 2. Calcular score consolidado
        score_consolidado = _calcular_score_consolidado(scores_data["scores"])
       
        # 3. Preparar dados para banco
        dados_completos = {
            **scores_data["scores"],
            "score_consolidado": score_consolidado["valor"] ,
            "classificacao_consolidada": score_consolidado["classificacao"]
        }
        
        # 4. Gravar no banco
        resultado_db = save_dashboard_scores(dados_completos)
        
        if resultado_db.get("status") == "success":
            logger.info(f"✅ Dashboard mercado salvo - Score: {score_consolidado['valor']:.1f}")
            
            return {
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                "id_registro": resultado_db["id"],
                "score_consolidado": score_consolidado["valor"],
                "classificacao": score_consolidado["classificacao"],
                "blocos": {
                    "ciclo": {
                        "score": scores_data["scores"]["score_ciclo"],
                        "classificacao": scores_data["scores"]["classificacao_ciclo"]
                    },
                    "momentum": {
                        "score": scores_data["scores"]["score_momentum"], 
                        "classificacao": scores_data["scores"]["classificacao_momentum"]
                    },
                    "tecnico": {
                        "score": scores_data["scores"]["score_tecnico"],
                        "classificacao": scores_data["scores"]["classificacao_tecnico"]
                    }
                }
            }
        else:
            return {
                "status": "error",
                "erro": "Falha ao salvar no banco",
                "detalhes": resultado_db.get("erro")
            }
        
    except Exception as e:
        logger.error(f"❌ Erro calcular dashboard mercado: {str(e)}")
        return {
            "status": "error",
            "erro": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

def obter_dash_mercado() -> dict:
    """
    Obtém último dashboard mercado com JSON pronto
    """
    try:
        
        import json
        
        ultimo = get_latest_dashboard_scores()
        
        if ultimo:
            # JSON pode vir como dict ou string do banco
            indicadores_json = ultimo["indicadores_json"]
            if isinstance(indicadores_json, str):
                indicadores_json = json.loads(indicadores_json)
            
            return {
                "status": "success",
                "id": ultimo["id"],
                "timestamp": ultimo["timestamp"].isoformat(),
                "score_consolidado": float(ultimo["score_consolidado"]),
                "classificacao": ultimo["classificacao_consolidada"],
                "blocos": {
                    "ciclo": {
                        "score": float(ultimo["score_ciclo"]),
                        "classificacao": ultimo["classificacao_ciclo"],
                        "indicadores": indicadores_json["ciclo"]
                    },
                    "momentum": {
                        "score": float(ultimo["score_momentum"]),
                        "classificacao": ultimo["classificacao_momentum"],
                        "indicadores": indicadores_json["momentum"]
                    },
                    "tecnico": {
                        "score": float(ultimo["score_tecnico"]),
                        "classificacao": ultimo["classificacao_tecnico"],
                        "indicadores": indicadores_json["tecnico"]
                    }
                }
            }
        else:
            return {
                "status": "error", 
                "erro": "Nenhum registro encontrado"
            }
            
    except Exception as e:
        logger.error(f"❌ Erro obter dashboard mercado: {str(e)}")
        return {
            "status": "error",
            "erro": str(e)
        }

def _calcular_score_consolidado(scores: dict) -> dict:
    """
    Calcula score consolidado com pesos definidos
    """
    try:
        # DEBUG: Ver o que está chegando
        logger.info(f"🔍 DEBUG scores completo: {scores}")
        
        score_ciclo = float(scores["score_ciclo"])
        score_momentum = float(scores["score_momentum"])
        score_tecnico = float(scores["score_tecnico"])
        
        # DEBUG: Ver valores extraídos
        logger.info(f"🔍 DEBUG valores: ciclo={score_ciclo}, momentum={score_momentum}, tecnico={score_tecnico}")
        
        score_consolidado = (
            (score_ciclo * 0.50) +
            (score_momentum * 0.20) +
            (score_tecnico * 0.30)
        )
        
        # DEBUG: Ver cálculo
        logger.info(f"🔍 DEBUG consolidado calculado: {score_consolidado}")
        
        resultado = round(score_consolidado, 1)
        logger.info(f"🔍 DEBUG resultado final: {resultado}")

    except Exception as e:
        logger.error(f"❌ Erro calcular score consolidado: {str(e)}")
        return {
            "valor": 5.0,
            "classificacao": "neutro"
        }