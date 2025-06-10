# app/services/utils/helpers/dashboard_home/aggregator.py

import logging
from datetime import datetime
from .header_helper import get_header_data
from .mercado_helper import get_mercado_data
from .risco_helper import get_risco_data

logger = logging.getLogger(__name__)

def collect_all_dashboard_data() -> dict:
    """
    Coleta dados de todos os módulos do dashboard
    
    Returns:
        dict com todos os campos + JSON consolidado
    """
    try:
        logger.info("🚀 Coletando dados completos do dashboard...")
        
        # Coletar dados de cada módulo
        header_data = get_header_data()
        mercado_data = get_mercado_data()
        risco_data = get_risco_data()
        
        # Verificar se algum módulo falhou
        erros = []
        if header_data["status"] != "success":
            erros.append(f"Header: {header_data['erro']}")
        if mercado_data["status"] != "success":
            erros.append(f"Mercado: {mercado_data['erro']}")
        if risco_data["status"] != "success":
            erros.append(f"Risco: {risco_data['erro']}")
        
        if erros:
            raise Exception(f"Falhas nos módulos: {'; '.join(erros)}")
        
        # Consolidar campos para PostgreSQL
        campos_consolidados = {
            **header_data["campos"],
            **mercado_data["campos"],
            **risco_data["campos"]
        }
        
        # Consolidar JSON para frontend
        json_consolidado = {
            "fase": "3_header_mercado_risco",
            "timestamp": datetime.utcnow().isoformat(),
            "header": header_data["json"],
            "mercado": mercado_data["json"],
            "risco": risco_data["json"],
            "metadata": {
                "fonte_header": header_data["fonte"],
                "fonte_mercado": mercado_data["fonte"],
                "fonte_risco": risco_data["fonte"],
                "modulos": ["header", "mercado", "risco"],
                "versao": "modular_v1"
            }
        }
        
        logger.info("✅ Dados consolidados com sucesso")
        
        return {
            "status": "success",
            "campos": campos_consolidados,
            "json": json_consolidado,
            "modulos_coletados": ["header", "mercado", "risco"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na consolidação: {str(e)}")
        return {
            "status": "error",
            "erro": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }