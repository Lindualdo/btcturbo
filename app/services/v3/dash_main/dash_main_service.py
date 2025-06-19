# app/services/v3/dash_main/dash_main_service.py

import logging
from datetime import datetime
from app.services.v3.analise_mercado import analise_mercado_service as analise_mercado
from app.services.scores import riscos
from app.services.v3.dash_main.utils.helpers.data_helper import save_dashboard, get_latest_dashboard
from app.services.v3.dash_main.utils.helpers.data_builder import build_dashboard_data, build_response_format
from app.services.v3.dash_main.utils.analise_alavancagem import executar_analise_alavancagem
from app.services.v3.dash_main.execucao_tatica_service import executar_execucao_tatica

logger = logging.getLogger(__name__)

def processar_dashboard() -> dict:
    """
    Dashboard V3 - POST: Processa 4 camadas e grava
    
    Status implementação:
    - [✅] Camada 1: Análise Mercado (score + ciclo)  
    - [✅] Camada 2: Análise Risco (health_factor + score)
    - [✅] Camada 3: Análise Alavancagem (real)
    - [✅] Camada 4: Execução Tática (real - NOVO)
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
        
        # CAMADA 4: Execução Tática (IMPLEMENTADO)
        dados_tatica = executar_execucao_tatica(dados_mercado, dados_risco, dados_alavancagem)
        logger.info(f"✅ Camada 4: {dados_tatica['estrategia']['decisao']} - {dados_tatica['estrategia']['setup_4h']}")
        
        # Construir dados formato compatível
        dashboard_data = build_dashboard_data(
            dados_mercado, dados_risco, dados_alavancagem, dados_tatica['estrategia']
        )
        
        # Adicionar dados técnicos ao resultado (nova seção)
        dashboard_data['tecnicos'] = dados_tatica['tecnicos']
        
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
                "estrategia": "✅ real - IMPLEMENTADO"
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
                "versao": "v3_4_camadas",
                "timestamp": datetime.utcnow().isoformat(),
                "erro": "Nenhum dashboard encontrado",
                "message": "Execute POST primeiro para gerar dados"
            }
        
        # Construir resposta
        response = build_response_format(dados)
        
        logger.info(f"✅ Dashboard obtido: ID {dados['id']}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Erro obter Dashboard V3: {str(e)}")
        return {
            "status": "error",
            "versao": "v3_4_camadas",
            "timestamp": datetime.utcnow().isoformat(),
            "erro": str(e),
            "message": "Falha obter Dashboard V3"
        }

def _executar_camada_risco() -> dict:
    """Executa Camada 2: Análise de Risco"""
    try:
        logger.info("🛡️ Executando Camada 2: Análise Risco...")
        
        resultado = riscos.obter_scores_risco()
        
        return {
            "score": resultado["scores"]["score_geral"],
            "classificacao": resultado["scores"]["classificacao_score"],
            "mvrv": resultado["indicadores"]["MVRV"]["valor"],
            "nupl": resultado["indicadores"]["NUPL"]["valor"],
            "health_factor": resultado["indicadores"]["Health_Factor"]["valor"],
            "dist_liquidacao": float(str(resultado["indicadores"]["Dist_Liquidacao"]["valor"]).replace("%", "")),
            "status": "success"
        }
        
    except Exception as e:
        error_msg = f"Erro Camada 2 Risco: {str(e)}"
        logger.error(f"❌ {error_msg}")
        raise Exception(error_msg)

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
                "camada_4_tatica": "✅ REAL - IMPLEMENTADO"
            },
            "database": "mesma_base_v2",
            "formato": "100%_compativel",
            "novas_funcionalidades": {
                "gate_system": "✅ 4 validações + overrides",
                "setup_detection": "✅ 4 setups de compra",
                "tecnicos_4h": "✅ RSI + EMA144",
                "estrategia_compra": "✅ implementada",
                "estrategia_venda": "🔄 mock - futura",
                "stop_loss": "🔄 mock - futura"
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "erro": str(e),
            "versao": "v3_4_camadas"
        }