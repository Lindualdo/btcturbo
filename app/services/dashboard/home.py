# app/services/dashboard/home.py - REFATORADO MODULAR

import logging
from datetime import datetime
from app.services.utils.helpers.dashboard_home.aggregator import collect_all_dashboard_data
from app.services.utils.helpers.dashboard_home.database_helper import insert_dashboard_data, get_latest_dashboard

logger = logging.getLogger(__name__)

def calcular_dashboard_home():
    """
    REFATORADO: Calcula e grava dados do dashboard (modular)
    
    Fluxo:
    1. Chama aggregator (que coleta de todos os helpers)
    2. Grava no PostgreSQL
    """
    try:
        logger.info("🚀 REFATORADO: Calculando dashboard modular...")
        
        # 1. Coletar dados de todos os módulos
        dados_consolidados = collect_all_dashboard_data()
        
        if dados_consolidados["status"] != "success":
            raise Exception(dados_consolidados["erro"])
        
        # 2. Gravar no PostgreSQL
        logger.info("💾 Gravando dados consolidados...")
        sucesso = insert_dashboard_data(
            campos=dados_consolidados["campos"],
            dashboard_json=dados_consolidados["json"]
        )
        
        if not sucesso:
            raise Exception("Falha ao gravar no PostgreSQL")
        
        # 3. Resposta de sucesso
        return {
            "status": "success",
            "versao": "modular_refatorado",
            "timestamp": datetime.utcnow().isoformat(),
            "modulos_processados": dados_consolidados["modulos_coletados"],
            "campos_gravados": list(dados_consolidados["campos"].keys()),
            "message": "Dashboard calculado e gravado (versão modular)"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no dashboard modular: {str(e)}")
        return {
            "status": "error",
            "versao": "modular_refatorado",
            "timestamp": datetime.utcnow().isoformat(),
            "erro": str(e),
            "message": "Falha no cálculo modular"
        }

def obter_dashboard_home():
    """
    REFATORADO: Obtém dados do dashboard (modular)
    """
    try:
        logger.info("🔍 REFATORADO: Obtendo dashboard modular...")
        
        # Buscar último registro
        dados = get_latest_dashboard()
        
        if not dados:
            return {
                "status": "error",
                "erro": "Nenhum dado encontrado",
                "message": "Execute POST /dashboard-home primeiro"
            }
        
        # Retornar JSON do dashboard
        dashboard_json = dados["dashboard_json"]
        
        # Se dashboard_json é string, converter para dict
        if isinstance(dashboard_json, str):
            import json
            dashboard_json = json.loads(dashboard_json)
        
        logger.info(f"✅ Dashboard modular obtido: {dados['created_at']}")
        
        return {
            "status": "success",
            "data": dashboard_json,
            "metadata": {
                "id": dados["id"],
                "created_at": dados["created_at"].isoformat(),
                "age_minutes": (datetime.utcnow() - dados["created_at"]).total_seconds() / 60,
                "versao": "modular_refatorado"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter dashboard modular: {str(e)}")
        return {
            "status": "error",
            "erro": str(e),
            "message": "Falha ao obter dashboard modular"
        }

def debug_dashboard_home():
    """
    REFATORADO: Debug simples
    """
    try:
        ultimo = get_latest_dashboard()
        
        return {
            "status": "success",
            "versao": "modular_refatorado",
            "ultimo_registro": {
                "id": ultimo["id"] if ultimo else None,
                "created_at": ultimo["created_at"].isoformat() if ultimo else None,
                "tem_dados": ultimo is not None
            },
            "arquitetura": {
                "helpers": ["header_helper", "mercado_helper"],
                "aggregator": "collect_all_dashboard_data",
                "database": "insert_dashboard_data"
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "erro": str(e)
        }