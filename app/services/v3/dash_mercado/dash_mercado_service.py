# app/services/v3/dash_main/dash_main_service.py

import logging
from datetime import datetime
from app.services.v3.analise_mercado import analise_mercado_service as analise_mercado
from app.services.scores import riscos
from app.services.v3.dash_main.utils.helpers.data_helper import save_dashboard, get_latest_dashboard
from app.services.v3.dash_main.utils.analise_alavancagem import executar_analise_alavancagem

logger = logging.getLogger(__name__)

def processar_dashboard() -> dict:
    """
    Dashboard V3 - POST: Processa 4 camadas e grava
    
    Status implementação:
    - [✅] Camada 1: Análise Mercado (score + ciclo)  
    - [✅] Camada 2: Análise Risco (health_factor + score)
    - [🔄] Camada 3: Análise Alavancagem (mock temporário)
    - [🔄] Camada 4: Execução Tática (mock temporário)
    """
    try:
        logger.info("🚀 Processando Dashboard V3 - POST")
        
        # CAMADA 1: Análise Mercado (real)
        dados_mercado = analise_mercado.executar_analise()
        logger.info(f"✅ Camada 1: Score {dados_mercado['score_mercado']} - {dados_mercado['classificacao_mercado']}")
        
        # CAMADA 2: Análise Risco (real)
        dados_risco = _executar_camada_risco()
        logger.info(f"✅ Camada 2: Score {dados_risco['score']} - {dados_risco['classificacao']}")
        
        # CAMADA 3: Análise Alavancagem (real)
        dados_alavancagem = executar_analise_alavancagem(dados_mercado, dados_risco)
        logger.info(f"✅ Camada 3: Alavancagem {dados_alavancagem.get('alavancagem_permitida', 0)}x")
        
        # CAMADA 4: Execução Tática (mock - TODO) 
        mock_estrategia = _get_mock_estrategia()
        logger.info("🔄 Camada 4: Mock estratégia")
        
        # Construir dados formato compatível
        dashboard_data = build_dashboard_data(
            dados_mercado, dados_risco, dados_alavancagem, mock_estrategia
        )
        
        # Salvar no PostgreSQL
        success = save_dashboard(dashboard_data)
        if not success:
            raise Exception("Falha ao salvar Dashboard")
        
        return {
            "status": "success",
            "versao": "v3_4_camadas",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Dashboard V3 processado e gravado",
            "camadas_processadas": {
                "mercado": "✅ real",
                "risco": "✅ real", 
                "alavancagem": "✅ real",
                "estrategia": "🔄 mock"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro processar Dashboard V3: {str(e)}")
        return {
            "status": "error",
            "versao": "v3_4_camadas",
            "timestamp": datetime.utcnow().isoformat(),
            "erro": str(e),
            "message": "Falha processar Dashboard V3"
        }

def obter_dashboard() -> dict:
    """
    Dashboard V3 - GET: Recupera último processado
    """
    try:
        logger.info("🔍 Obtendo Dashboard V3 - GET")
        
        # Buscar último registro
        dados = get_latest_dashboard()
        
        if not dados:
            return {
                "status": "error",
                "erro": "Nenhum dashboard V3 encontrado",
                "message": "Execute POST /api/v3/dash-main primeiro"
            }
        
        # Converter JSON se necessário
        dashboard_json = dados["dashboard_json"]
        if isinstance(dashboard_json, str):
            import json
            dashboard_json = json.loads(dashboard_json)
        
        # Retornar formato esperado
        return build_response_format(
            {"json": dashboard_json},
            dados["id"],
            dados["created_at"]
        )
        
    except Exception as e:
        logger.error(f"❌ Erro obter Dashboard V3: {str(e)}")
        return {
            "status": "error",
            "erro": str(e),
            "message": "Falha obter Dashboard V3"
        }

def _executar_camada_risco() -> dict:
    """Camada 2: Análise Risco - usa função existente"""
    try:
        logger.info("🛡️ Executando Camada 2: Análise Risco...")
        
        resultado = riscos.calcular_score()
        
        if resultado.get("status") != "success":
            error_msg = f"Falha calcular_score_risco: {resultado.get('erro', 'erro desconhecido')}"
            logger.error(f"❌ {error_msg}")
            raise Exception(error_msg)
        
        # Adaptar formato
        return {
            "score": resultado["score_consolidado"],
            "classificacao": resultado["classificacao_consolidada"],
            "health_factor": resultado["indicadores"]["Health_Factor"]["valor"],
            "dist_liquidacao": resultado["indicadores"]["Dist_Liquidacao"]["valor"], 
            "status": "success"
        }
        
    except Exception as e:
        error_msg = f"Erro Camada 2 Risco: {str(e)}"
        logger.error(f"❌ {error_msg}")
        raise Exception(error_msg)

def _get_mock_estrategia() -> dict:
    """Mock Camada 4 - TODO: implementar decisão real"""
    logger.warning("🔄 Usando dados mock para Camada 4 - implementar execução tática")
    return {
        "decisao": "AGUARDAR_IMPLEMENTACAO",
        "setup_4h": "INDEFINIDO",
        "urgencia": "baixa",
        "justificativa": "Camada 4 não implementada"
    }

def debug_dashboard() -> dict:
    """Debug status implementação"""
    try:
        ultimo = get_latest_dashboard()
        
        return {
            "status": "success",
            "versao": "v3_4_camadas",
            "ultimo_registro": {
                "id": ultimo["id"] if ultimo else None,
                "created_at": ultimo["created_at"].isoformat() if ultimo else None,
                "tem_dados": ultimo is not None
            },
            "implementacao": {
                "camada_1_mercado": "✅ REAL",
                "camada_2_risco": "✅ REAL", 
                "camada_3_alavancagem": "✅ REAL",
                "camada_4_tatica": "🔄 MOCK - TODO"
            },
            "database": "mesma_base_v2",
            "formato": "100%_compativel"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "erro": str(e),
            "versao": "v3_4_camadas"
        }