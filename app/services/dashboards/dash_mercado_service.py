# source: app/services/dashboards/dash_mercado_service.py

import logging
from datetime import datetime
from .dash_mercado.main_functions import save_dashboard_scores, get_latest_dashboard_scores
from app.services.scores.ciclos import calcular_score as calcular_score_ciclo
from app.services.scores.momentum import calcular_score as calcular_score_momentum
from app.services.scores.tecnico  import calcular_score as calcular_score_tecnico


logger = logging.getLogger(__name__)

def processar_dash_mercado() -> dict:
    try:

        # 1 - Busca os scores calculados (todos os blocos)
        scores = get_scores_data()
       
        # 2. Calcula o score consolidado
        logger.info("🔄 Coletando e calculando scores...")
        score_consolidado = _calcular_score_consolidado(scores)

        # 3. Preparar dados para banco
        dados_completos = {
            **scores,
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
                        "score": scores["ciclo"]["score_consolidado"],
                        "classificacao": scores["ciclo"]["classificacao_consolidada"]
                    },
                    "momentum": {
                        "score": scores["momentum"]["score_consolidado"], 
                        "classificacao": scores["momentum"]["classificacao_consolidada"]
                    },
                    "tecnico": {
                        "score": scores["tecnico"]["score_consolidado"],
                        "classificacao": scores["tecnico"]["classificacao_consolidada"]
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

def get_scores_data() -> dict:

    # 1. Coletar scores
    ciclo = calcular_score_ciclo()
    tecnico = calcular_score_tecnico()
    momentum = calcular_score_momentum()

    return {
        "ciclo": ciclo,
        "momentum": momentum, 
        "tecnico": tecnico
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
  
    try:
        
        score_ciclo = float(scores["ciclo"]["score_consolidado"])
        score_momentum = float(scores["momentum"]["score_consolidado"])
        score_tecnico = float(scores["tecnico"]["score_consolidado"])

        # DEBUG: Ver valores extraídos
        logger.info(f"🔍 DEBUG valores: ciclo={score_ciclo}, momentum={score_momentum}, tecnico={score_tecnico}")
        
        score_consolidado = (
            (score_ciclo * 0.50) +
            (score_momentum * 0.20) +
            (score_tecnico * 0.30)
        )

        # Determinar classificação
        if score_consolidado >= 8.0:
            classificacao = "ótimo"
        elif score_consolidado >= 6.0:
            classificacao = "bom"
        elif score_consolidado >= 4.0:
            classificacao = "neutro"
        elif score_consolidado >= 2.0:
            classificacao = "ruim"
        else:
            classificacao = "crítico"
        
        return {
            "valor": round(score_consolidado, 1),
            "classificacao": classificacao
        }

    except Exception as e:
        logger.error(f"❌ Erro calcular score consolidado: {str(e)}")
        return {
            "valor": 0,
            "classificacao": "neutro"
        }