# app/services/v3/dash_mercado/utils/data_collector.py

import logging

logger = logging.getLogger(__name__)

def collect_all_blocks_data() -> dict:
    """
    Coleta dados dos 3 blocos usando APIs existentes
    
    Returns:
        dict: {"status": "success/error", "dados": {ciclo, momentum, tecnico}}
    """
    try:
        logger.info("📥 Coletando dados dos indicadores...")
        
        # Importar APIs existentes
        from app.services.indicadores import ciclos as indicadores_ciclos
        from app.services.indicadores import momentum as indicadores_momentum  
        from app.services.indicadores import tecnico as indicadores_tecnico
        
        # Coletar dados de cada bloco
        dados_ciclo = _collect_ciclo_data(indicadores_ciclos)
        dados_momentum = _collect_momentum_data(indicadores_momentum)
        dados_tecnico = _collect_tecnico_data(indicadores_tecnico)
        
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

def _collect_ciclo_data(indicadores_ciclos) -> dict:
    """Coleta dados do bloco CICLO"""
    try:
        dados = indicadores_ciclos.obter_indicadores()
        
        if dados.get("status") == "success":
            logger.info("✅ Dados CICLO coletados")
            return dados["indicadores"]
        else:
            logger.error("❌ Falha coleta CICLO")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro _collect_ciclo_data: {str(e)}")
        return None

def _collect_momentum_data(indicadores_momentum) -> dict:
    """Coleta dados do bloco MOMENTUM"""
    try:
        dados = indicadores_momentum.obter_indicadores()
        
        if dados.get("status") == "success":
            logger.info("✅ Dados MOMENTUM coletados")
            return dados["indicadores"]
        else:
            logger.error("❌ Falha coleta MOMENTUM")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro _collect_momentum_data: {str(e)}")
        return None

def _collect_tecnico_data(indicadores_tecnico) -> dict:
    """Coleta dados do bloco TÉCNICO"""
    try:
        dados = indicadores_tecnico.obter_indicadores()
        
        if dados.get("status") == "success":
            logger.info("✅ Dados TÉCNICO coletados")
            return dados["indicadores"]
        else:
            logger.error("❌ Falha coleta TÉCNICO")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro _collect_tecnico_data: {str(e)}")
        return None