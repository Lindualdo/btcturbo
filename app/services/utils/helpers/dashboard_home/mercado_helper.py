# app/services/utils/helpers/dashboard_home/mercado_helper.py

import logging
from app.services.analises.analise_mercado import calcular_analise_mercado
from app.services.indicadores import ciclos

logger = logging.getLogger(__name__)

def get_mercado_data() -> dict:
    """
    Coleta dados do score de mercado: score, classificação, MVRV, NUPL
    
    Returns:
        dict com campos do score mercado ou erro
    """
    try:
        logger.info("📊 Coletando dados do score mercado...")
        
        # Buscar score mercado
        dados_mercado = calcular_analise_mercado()
        
        if dados_mercado.get("status") != "success":
            raise Exception(f"Dados de mercado indisponíveis: {dados_mercado.get('erro')}")
        
        # Buscar dados de ciclos para MVRV e NUPL
        dados_ciclos = ciclos.obter_indicadores()
        
        if dados_ciclos.get("status") != "success":
            raise Exception(f"Dados de ciclos indisponíveis: {dados_ciclos.get('erro')}")
        
        # Extrair campos
        score_mercado = float(dados_mercado["score_consolidado"])
        score_mercado_classificacao = dados_mercado["classificacao"]
        mvrv_valor = float(dados_ciclos["indicadores"]["MVRV_Z"]["valor"])
        nupl_valor = float(dados_ciclos["indicadores"]["NUPL"]["valor"]) if dados_ciclos["indicadores"]["NUPL"]["valor"] is not None else 0.0
        
        logger.info(f"✅ Mercado: Score={score_mercado:.1f} ({score_mercado_classificacao}), MVRV={mvrv_valor:.2f}, NUPL={nupl_valor:.3f}")
        
        return {
            "status": "success",
            "campos": {
                "score_mercado": score_mercado,
                "score_mercado_classificacao": score_mercado_classificacao,
                "mvrv_valor": mvrv_valor,
                "nupl_valor": nupl_valor
            },
            "json": {
                "score": score_mercado,
                "score_formatado": f"{score_mercado:.1f}",
                "classificacao": score_mercado_classificacao,
                "mvrv": mvrv_valor,
                "mvrv_formatado": f"{mvrv_valor:.2f}",
                "nupl": nupl_valor,
                "nupl_formatado": f"{nupl_valor:.3f}"
            },
            "fonte": "analise-mercado + obter-indicadores/ciclos"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no score mercado: {str(e)}")
        return {
            "status": "error",
            "erro": str(e),
            "campos": {
                "score_mercado": 0.0,
                "score_mercado_classificacao": "erro",
                "mvrv_valor": 0.0,
                "nupl_valor": 0.0
            }
        }