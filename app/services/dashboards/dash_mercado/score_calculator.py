# source: app/services/dashboards/dash_mercado/score_calculator.py

import logging
 # Importar funções de score existentes
from app.services.scores.ciclos import calcular_score as calcular_score_ciclo
from app.services.scores.momentum import calcular_score as calcular_score_momentum
from app.services.scores.tecnico  import calcular_score as calcular_score_tecnico

logger = logging.getLogger(__name__)

def calculate_all_scores() -> dict:

    try:
        logger.info("🧮 Calculando scores dos 3 blocos...")

        # Calcular scores individuais
        resultado_ciclo = calcular_score_ciclo()
        resultado_momentum =  calcular_score_momentum()
        resultado_tecnico = calcular_score_tecnico()
        
        # Verificar se todos os scores foram calculados
        if not resultado_ciclo or not resultado_momentum or not resultado_tecnico:
            return {
                "status": "error",
                "erro": "Falha no cálculo de um ou mais scores"
            }
        
        # Consolidar todos os scores

        logger.info("🧮 Calculando scores dos 3 blocos...")

        scores_consolidados = {
            "score_ciclo": resultado_ciclo["score_consolidado"] ,
            "classificacao_ciclo": resultado_ciclo["classificacao_consolidada"],
            "score_momentum": resultado_momentum["score_consolidado"],
            "classificacao_momentum": resultado_momentum["classificacao_consolidada"],
            "score_tecnico": resultado_tecnico["score_consolidado"], 
            "classificacao_tecnico": resultado_tecnico["classificacao_consolidada"]
        }
        
        logger.info("✅ Todos os scores calculados")
        return {
            "status": "success",
            "scores": scores_consolidados
        }
        
    except Exception as e:
        logger.error(f"❌ Erro calculate_all_scores: {str(e)}")
        return {
            "status": "error",
            "erro": str(e)
        }