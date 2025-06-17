# services/v3/data_collector.py
import logging
from .utils.analise.mercado.analise_mercado import executar_analise_mercado
from .utils.analise.risco.analise_risco import executar_analise_risco
from .utils.analise.alavancagem.analise_alavancagem import executar_analise_alavancagem
from .utils.analise.tatica.setup_hunter import executar_analise_tatica

logger = logging.getLogger(__name__)

def collect_all_data_v3() -> dict:
    """
    Coleta dados das 4 camadas conforme overview
    Fluxo: Mercado → Risco → Alavancagem → Tática
    """
    try:
        logger.info("📊 Coletando dados V3 - 4 camadas sequenciais")
        
        # 1. ANÁLISE MERCADO (Score + Ciclo + Indicadores)
        mercado_data = executar_analise_mercado()
        logger.info(f"✅ Mercado: Score {mercado_data['score']} - Ciclo {mercado_data['ciclo']}")
        
        # 2. ANÁLISE RISCO (Score + Health Factor)
        risco_data = executar_analise_risco()
        logger.info(f"✅ Risco: Score {risco_data['score']} - HF {risco_data['health_factor']}")
        
        # 3. ANÁLISE ALAVANCAGEM (Limite baseado em Mercado + Risco + IFR)
        alavancagem_data = executar_analise_alavancagem(mercado_data, risco_data)
        logger.info(f"✅ Alavancagem: Limite {alavancagem_data['limite_max']}x")
        
        # 4. ANÁLISE TÁTICA (Setup + Estratégia final)
        tatica_data = executar_analise_tatica(mercado_data, risco_data, alavancagem_data)
        logger.info(f"✅ Tática: {tatica_data['decisao']} - Setup {tatica_data['setup']}")
        
        # Consolidar todos os dados
        all_data = {
            "mercado": mercado_data,
            "risco": risco_data,
            "alavancagem": alavancagem_data,
            "tatica": tatica_data,
            "timestamp": mercado_data["timestamp"]  # Timestamp unificado
        }
        
        logger.info("✅ Coleta V3 concluída - 4 camadas")
        return all_data
        
    except Exception as e:
        logger.error(f"❌ Erro coleta dados V3: {str(e)}")
        raise Exception(f"Falha na coleta de dados: {str(e)}")