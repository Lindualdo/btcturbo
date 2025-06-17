# services/v3/dash_home_service.py
import logging
from datetime import datetime
from .utils.data_collector import collect_all_data_v3
from .utils.gate_system import apply_gate_system
from .utils.gera_json import generate_dashboard_json_v3
from .utils.database_helper import save_dashboard_v3, get_latest_dashboard_v3

logger = logging.getLogger(__name__)

def calcular_dashboard_v3() -> dict:
    """
    Orquestrador principal V3 - Fluxo overview completo
    1. Coleta dados (4 camadas)
    2. Gate system
    3. Gera JSON
    4. Salva banco
    """
    try:
        logger.info("🚀 Calculando Dashboard V3...")
        
        # 1. Coleta dados das 4 camadas (sequencial conforme overview)
        all_data = collect_all_data_v3()
        logger.info("✅ Dados coletados - 4 camadas")
        
        # 2. Gate system centralizado
        gate_result = apply_gate_system(all_data)
        if gate_result["blocked"]:
            logger.warning(f"🛡️ Gate acionado: {gate_result['reason']}")
            return gate_result["response"]
        
        # 3. Gera JSON final compatível V2
        dashboard_json = generate_dashboard_json_v3(all_data)
        
        # 4. Salva no banco (tabela dashboard_decisao_v2)
        saved_id = save_dashboard_v3(dashboard_json, all_data)
        
        logger.info(f"✅ Dashboard V3 calculado - ID: {saved_id}")
        
        return {
            "status": "success",
            "message": "Dashboard V3 calculado",
            "data": dashboard_json,
            "metadata": {
                "id": saved_id,
                "versao": "v3_overview_compliant",
                "created_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro calcular Dashboard V3: {str(e)}")
        return {
            "status": "error",
            "erro": str(e),
            "message": "Falha ao calcular Dashboard V3"
        }

def obter_dashboard_v3() -> dict:
    """GET - Retorna último dashboard calculado"""
    try:
        dados = get_latest_dashboard_v3()
        if not dados:
            return {
                "status": "error",
                "message": "Nenhum dashboard encontrado. Execute POST primeiro."
            }
        
        return {
            "status": "success",
            "data": dados["dashboard_json"],
            "metadata": {
                "id": dados["id"],
                "created_at": dados["created_at"].isoformat(),
                "age_minutes": (datetime.utcnow() - dados["created_at"]).total_seconds() / 60,
                "versao": "v3_overview_compliant"
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "erro": str(e)
        }

def debug_dashboard_v3() -> dict:
    """Debug sistema V3"""
    return {
        "status": "success",
        "versao": "v3_overview_compliant",
        "arquitetura": {
            "camadas": ["mercado", "risco", "alavancagem", "tatica"],
            "fluxo": "sequencial_overview",
            "gate_system": "centralizado",
            "database": "dashboard_decisao_v2"
        }
    }