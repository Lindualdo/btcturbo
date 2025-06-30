# source: app/services/dashboards/dash_mercado_service.py

import logging
from datetime import datetime
from .dash_mercado.main_functions import save_dashboard_scores, get_latest_dashboard_scores
from .dash_mercado.gatilhos_score import aplicar_gatilhos_score  # ← NOVO IMPORT
from app.services.scores.ciclos import calcular_score as calcular_score_ciclo
from app.services.scores.momentum import calcular_score as calcular_score_momentum
from app.services.scores.tecnico  import calcular_score as calcular_score_tecnico

logger = logging.getLogger(__name__)

def processar_dash_mercado(aplicar_gatilho: bool = True) -> dict:
    try:
        # 1 - Busca os scores calculados (todos os blocos)
        scores = _get_scores_data()
       
        # 2. Calcula o score consolidado COM PESOS PADRÃO
        logger.info("🔄 Coletando e calculando scores...")
        score_consolidado = _calcular_score_consolidado(scores)

        # 3. Preparar dados para aplicação de gatilhos
        dados_completos = {
            **scores,
            "score_consolidado": score_consolidado["valor"],
            "classificacao_consolidada": score_consolidado["classificacao"]
        }
        
        # 4. ← APLICAR GATILHOS CONDICIONALMENTE
        if aplicar_gatilho:
            logger.info("🎯 Aplicando gatilhos de modificação de pesos...")
            dados_completos = aplicar_gatilhos_score(dados_completos)
            
            # Verificar se gatilhos funcionaram corretamente
            if "pesos_utilizados" not in dados_completos or "gatilhos_acionados" not in dados_completos:
                logger.error("❌ Falha nos gatilhos - campos obrigatórios ausentes")
                return {
                    "status": "error",
                    "erro": "Sistema de gatilhos falhou - dados incompletos",
                    "timestamp": datetime.utcnow().isoformat()
                }
        else:
            logger.info("⚪ Gatilhos desabilitados - usando pesos padrão")
            dados_completos["pesos_utilizados"] = {"ciclo": 0.50, "momentum": 0.20, "tecnico": 0.30}
            dados_completos["gatilhos_acionados"] = "DESABILITADO"
            
        logger.info(f"📊 Pesos finais: {dados_completos['pesos_utilizados']}")
        logger.info(f"🎯 Gatilho: {dados_completos['gatilhos_acionados']}")
        
        # 5. Gravar no banco (com score já ajustado pelos gatilhos)
        resultado_db = save_dashboard_scores(dados_completos)
        
        if resultado_db.get("status") == "success":
            # Log do resultado final
            gatilho_info = dados_completos.get("gatilho_aplicado", {})
            if gatilho_info.get("ativado"):
                logger.info(f"✅ Dashboard salvo COM GATILHO: {gatilho_info.get('tipo')} - Score: {dados_completos['score_consolidado']:.1f}")
            else:
                logger.info(f"✅ Dashboard salvo SEM GATILHO - Score: {dados_completos['score_consolidado']:.1f}")
            
            return {
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                "id_registro": resultado_db["id"],
                "score_consolidado": dados_completos["score_consolidado"],
                "classificacao": dados_completos["classificacao_consolidada"],
                "gatilho": gatilho_info,  # ← NOVO: Info do gatilho aplicado
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

# Resto das funções mantém igual
def _get_scores_data() -> dict:
    # [Código existente sem alteração]
    ciclo = calcular_score_ciclo()
    tecnico = calcular_score_tecnico()
    momentum = calcular_score_momentum()

    return {
        "ciclo": ciclo,
        "momentum": momentum, 
        "tecnico": tecnico
    }

def obter_dash_mercado() -> dict:
    # [Código existente sem alteração]
    try:
        import json
        
        dash_mercado = get_latest_dashboard_scores()
        
        if dash_mercado:
            indicadores_json = dash_mercado["indicadores_json"]
            if isinstance(indicadores_json, str):
                indicadores_json = json.loads(indicadores_json)
            
            return {
                "status": "success",
                "id": dash_mercado["id"],
                "timestamp": dash_mercado["timestamp"].isoformat(),
                "score_consolidado": float(dash_mercado["score_consolidado"]),
                "classificacao": dash_mercado["classificacao_consolidada"],
                **indicadores_json
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
    # [Código existente sem alteração]
    try:
        score_ciclo = float(scores["ciclo"]["score_consolidado"])
        score_momentum = float(scores["momentum"]["score_consolidado"])
        score_tecnico = float(scores["tecnico"]["score_consolidado"])

        logger.info(f"🔍 DEBUG valores: ciclo={score_ciclo}, momentum={score_momentum}, tecnico={score_tecnico}")
        
        score_consolidado = (
            (score_ciclo * 0.50) +
            (score_momentum * 0.20) +
            (score_tecnico * 0.30)
        )

        if score_consolidado >= 80.0:
            classificacao = "ótimo"
        elif score_consolidado >= 60.0:
            classificacao = "bom"
        elif score_consolidado >= 40.0:
            classificacao = "neutro"
        elif score_consolidado >= 20.0:
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