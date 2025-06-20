# source: app/services/dashboards/dash_mercado/data_collector.py

import logging

# Importar APIs existentes
from app.services.indicadores import ciclos as indicadores_ciclos
from app.services.indicadores import momentum as indicadores_momentum  
from app.services.indicadores import tecnico as indicadores_tecnico

logger = logging.getLogger(__name__)

def collect_all_blocks_data() -> dict:
    """
    Coleta dados dos 3 blocos usando APIs existentes
    
    Returns:
        dict: {"status": "success/error", "dados": {ciclo, momentum, tecnico}}
    """
    try:
        logger.info("📥 Coletando dados dos indicadores...")

        # Coletar dados de cada bloco
        dados_ciclo = indicadores_ciclos.obter_indicadores()
        dados_momentum = indicadores_momentum.obter_indicadores()
        dados_tecnico = indicadores_tecnico.obter_indicadores()
        
        # Verificar se todos os dados foram coletados
        if not dados_ciclo or not dados_momentum or not dados_tecnico:
            return {
                "status": "error",
                "erro": "Falha na coleta de um ou mais blocos de dados"
            }
        
        return {
            "status": "success",
            "dados": {
                "ciclo": dados_ciclo,
                "momentum": dados_momentum, 
                "tecnico": dados_tecnico
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro collect_all_blocks_data: {str(e)}")
        return {
            "status": "error",
            "erro": str(e)
        }