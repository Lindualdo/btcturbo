# app/services/utils/helpers/dashboard_home/risco_helper.py

import logging
from app.services.analises.analise_risco import calcular_analise_risco

logger = logging.getLogger(__name__)

def get_risco_data() -> dict:
    """
    Coleta dados do score de risco: score, classificação, health factor, dist liquidação
    
    Returns:
        dict com campos do score risco ou erro
    """
    try:
        logger.info("📊 Coletando dados do score risco...")
        
        # Buscar análise de risco
        dados_risco = calcular_analise_risco()
        
        if dados_risco.get("status") != "success":
            raise Exception(f"Dados de risco indisponíveis: {dados_risco.get('erro')}")
        
        # Extrair campos principais
        score_risco = float(dados_risco["score_consolidado"])
        score_risco_classificacao = dados_risco["classificacao"]
        
        # Extrair health factor e dist liquidação do breakdown
        composicao = dados_risco.get("composicao", {})
        breakdown = composicao.get("breakdown", {})
        
        # Health Factor
        hf_data = breakdown.get("health_factor", {})
        health_factor = float(hf_data.get("valor_display", "0").replace("N/A", "0"))
        
        # Distância Liquidação (remover % e converter)
        dl_data = breakdown.get("dist_liquidacao", {})
        dist_liquidacao_str = dl_data.get("valor_display", "0%")
        dist_liquidacao = float(dist_liquidacao_str.replace("%", "").replace("N/A", "0"))
        
        logger.info(f"✅ Risco: Score={score_risco:.1f} ({score_risco_classificacao}), HF={health_factor:.2f}, Dist={dist_liquidacao:.1f}%")
        
        return {
            "status": "success",
            "campos": {
                "score_risco": score_risco,
                "score_risco_classificacao": score_risco_classificacao,
                "health_factor": health_factor,
                "dist_liquidacao": dist_liquidacao
            },
            "json": {
                "score": score_risco,
                "score_formatado": f"{score_risco:.1f}",
                "classificacao": score_risco_classificacao,
                "health_factor": health_factor,
                "health_factor_formatado": f"{health_factor:.2f}",
                "dist_liquidacao": dist_liquidacao,
                "dist_liquidacao_formatado": f"{dist_liquidacao:.1f}%"
            },
            "modulo": "risco",
            "fonte": "analise-risco"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no score risco: {str(e)}")
        return {
            "status": "error",
            "erro": str(e),
            "campos": {
                "score_risco": 0.0,
                "score_risco_classificacao": "erro",
                "health_factor": 0.0,
                "dist_liquidacao": 0.0
            }
        }