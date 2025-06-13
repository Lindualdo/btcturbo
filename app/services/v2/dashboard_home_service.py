# app/services/v2/dashboard_home_service.py

import logging
from datetime import datetime
from app.services.utils.helpers.v2.dashboard_home.data_collector import collect_all_data
from app.services.utils.helpers.v2.dashboard_home.cycle_analyzer import identify_cycle
from app.services.utils.helpers.v2.dashboard_home.setup_detector import detect_setup_4h
from app.services.utils.helpers.v2.dashboard_home.validation_gates import apply_protection_gates
from app.services.utils.helpers.v2.dashboard_home.decision_matrix import apply_decision_matrix
from app.services.utils.helpers.v2.dashboard_home.database_v2_helper import (
    save_dashboard_v2, get_latest_dashboard_v2
)

logger = logging.getLogger(__name__)

def calcular_dashboard_v2() -> dict:
    """
    Calcula dashboard V2 com fluxo otimizado
    
    Fluxo:
    1. UMA busca de todos os dados
    2. Processamento sequencial
    3. UMA gravação no banco
    """
    try:
        logger.info("🚀 Calculando Dashboard V2...")
        
        # 1. Coletar TODOS os dados (uma única vez)
        all_data = collect_all_data()
        logger.info("✅ Dados coletados")
        
        # 2. Processamento sequencial
        cycle_info = identify_cycle(all_data)
        setup_info = detect_setup_4h(all_data)
        protection_result = apply_protection_gates(all_data)
        
        # Se proteção acionada, retorna imediatamente
        if protection_result["action_required"]:
            final_decision = protection_result
            logger.info(f"🛡️ Proteção acionada: {protection_result['decision']}")
        else:
            # Aplica matriz de decisão normal
            final_decision = apply_decision_matrix(cycle_info, setup_info, all_data)
            logger.info(f"🎯 Decisão matriz: {final_decision['decision']}")
        
        # 3. Consolidar resultado final
        dashboard_result = _build_final_result(
            all_data, cycle_info, setup_info, final_decision
        )
        
        # 4. Salvar no banco
        success = save_dashboard_v2(dashboard_result)
        if not success:
            raise Exception("Falha ao salvar no PostgreSQL")
        
        return {
            "status": "success",
            "versao": "v2_otimizado",
            "timestamp": datetime.utcnow().isoformat(),
            "data": dashboard_result["json"],
            "message": "Dashboard V2 calculado com sucesso"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro Dashboard V2: {str(e)}")
        return {
            "status": "error",
            "versao": "v2_otimizado", 
            "timestamp": datetime.utcnow().isoformat(),
            "erro": str(e),
            "message": "Falha no cálculo Dashboard V2"
        }

def obter_dashboard_v2() -> dict:
    """
    Obtém último dashboard V2 calculado
    """
    try:
        logger.info("🔍 Obtendo Dashboard V2...")
        
        dados = get_latest_dashboard_v2()
        
        if not dados:
            return {
                "status": "error",
                "erro": "Nenhum dashboard V2 encontrado",
                "message": "Execute POST /api/v2/dashboard-home primeiro"
            }
        
        # Converter JSON se necessário
        dashboard_json = dados["dashboard_json"]
        if isinstance(dashboard_json, str):
            import json
            dashboard_json = json.loads(dashboard_json)
        
        return {
            "status": "success",
            "data": dashboard_json,
            "metadata": {
                "id": dados["id"],
                "created_at": dados["created_at"].isoformat(),
                "age_minutes": (datetime.utcnow() - dados["created_at"]).total_seconds() / 60,
                "versao": "v2_otimizado"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro obter Dashboard V2: {str(e)}")
        return {
            "status": "error",
            "erro": str(e),
            "message": "Falha ao obter Dashboard V2"
        }

def debug_dashboard_v2() -> dict:
    """
    Debug do sistema V2
    """
    try:
        ultimo = get_latest_dashboard_v2()
        
        return {
            "status": "success",
            "versao": "v2_otimizado",
            "ultimo_registro": {
                "id": ultimo["id"] if ultimo else None,
                "created_at": ultimo["created_at"].isoformat() if ultimo else None,
                "tem_dados": ultimo is not None
            },
            "arquitetura": {
                "collectors": ["data_collector"],
                "processors": ["cycle_analyzer", "setup_detector", "validation_gates", "decision_matrix"],
                "database": "database_v2_helper"
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "erro": str(e),
            "versao": "v2_otimizado"
        }

def _build_final_result(all_data: dict, cycle_info: dict, setup_info: dict, final_decision: dict) -> dict:
    """
    Constrói resultado final consolidado
    """
    # Campos para PostgreSQL (essenciais apenas)
    campos = {
        "btc_price": all_data["btc_price"],
        "score_mercado": all_data["score_mercado"],
        "score_risco": all_data["score_risco"],
        "ciclo_atual": cycle_info["cycle"],
        "setup_4h": setup_info["setup"],
        "decisao_final": final_decision["decision"],
        "alavancagem_atual": all_data["alavancagem_atual"],
        "health_factor": all_data["health_factor"],
        "ema_distance": all_data["ema_distance"],
        "rsi_diario": all_data["rsi_diario"]
    }
    
    # JSON para frontend (estruturado)
    json_response = {
        "timestamp": datetime.utcnow().isoformat(),
        "versao": "v2_dashboard",
        "header": {
            "btc_price": all_data["btc_price"],
            "alavancagem_atual": all_data["alavancagem_atual"],
            "status": "operacional"
        },
        "scores": {
            "mercado": all_data["score_mercado"],
            "risco": all_data["score_risco"],
            "mvrv": all_data["mvrv"],
            "health_factor": all_data["health_factor"]
        },
        "estrategia": {
            "decisao": final_decision["decision"],
            "ciclo": cycle_info["cycle"],
            "setup_4h": setup_info["setup"],
            "justificativa": final_decision.get("justificativa", ""),
            "urgencia": final_decision.get("urgencia", "media")
        },
        "tecnicos": {
            "ema_distance": all_data["ema_distance"],
            "rsi_diario": all_data["rsi_diario"],
            "preco_ema144": all_data["ema_valor"]
        },
        "alavancagem": {
            "atual": all_data["alavancagem_atual"],
            "permitida": all_data["alavancagem_permitida"],
            "valor_disponivel": all_data["valor_disponivel"],
            "dist_liquidacao": all_data["dist_liquidacao"]
        }
    }
    
    return {
        "campos": campos,
        "json": json_response
    }