# source: app/services/dashboards/dash_main_service.py

import logging
from datetime import datetime
from app.services.scores import riscos
from .dash_main.helpers.data_helper import save_dashboard, get_latest_dashboard
from .dash_main.helpers.data_builder import build_dashboard_data, build_response_format
from .dash_main.analise_alavancagem import executar_analise_alavancagem
from .dash_main.analise_tecnica.analise_tecnica_service import executar_analise
from  app.services.utils.helpers.postgres.mercado.database_helper import get_ciclo_mercado

logger = logging.getLogger(__name__)

def processar_dash_main() -> dict:
    """
    Dashboard - POST: Processa 4 camadas e grava
    """
    try:
        logger.info("🚀 Processando Dash-main - POST")
        
        # CAMADA 1: Análise Mercado
        dados_mercado =  get_ciclo_mercado()
        logger.info(f"✅ Camada 1: Score {dados_mercado['score_mercado']} - {dados_mercado['classificacao_mercado']}")
        
        # CAMADA 2: Análise Risco
        dados_risco = _executar_camada_risco()
        logger.info(f"✅ Camada 2: Score {dados_risco['score']} - {dados_risco['classificacao']}")
        
        # CAMADA 3: Análise Alavancagem
        alavancagem_permitida = dados_mercado["ciclo_detalhes"]["alavancagem"]
        dados_alavancagem = executar_analise_alavancagem(alavancagem_permitida)
        logger.info(f"✅ Camada 3: Alavancagem {dados_alavancagem.get('alavancagem_permitida', 0)}x")
        
        # CAMADA 4: Execução Tática (analise tecnica e setups)
        logger.info("🎯 Executando Camada 4: Analise Tática...")
        
        dados_tatica = executar_analise(dados_mercado, dados_risco, dados_alavancagem)
        
        # DEBUG: Verificar estrutura retornada
        logger.info(f"🔍 DEBUG Camada 4 - Tipo: {type(dados_tatica)}")
        logger.info(f"🔍 DEBUG Camada 4 - Keys: {list(dados_tatica.keys()) if isinstance(dados_tatica, dict) else 'Não é dict'}")
        
        if isinstance(dados_tatica, dict):
            if 'tecnicos' in dados_tatica:
                logger.info(f"🔍 DEBUG Técnicos: {dados_tatica['tecnicos']}")
            else:
                logger.error("❌ 'tecnicos' ausente em dados_tatica")
                raise Exception("Camada 4: 'tecnicos' ausente")
                
            if 'estrategia' in dados_tatica:
                logger.info(f"🔍 DEBUG Estratégia: {dados_tatica['estrategia']}")
            else:
                logger.error("❌ 'estrategia' ausente em dados_tatica")
                raise Exception("Camada 4: 'estrategia' ausente")
        else:
            logger.error(f"❌ Camada 4 retornou tipo inválido: {type(dados_tatica)}")
            raise Exception(f"Camada 4: tipo inválido {type(dados_tatica)}")
        
        logger.info(f"✅ Camada 4: {dados_tatica['estrategia']['decisao']} - {dados_tatica['estrategia']['setup']}")
        
        # Construir dados formato compatível
        logger.info("🔧 Construindo dashboard data...")
        dashboard_data = build_dashboard_data(
            dados_mercado, dados_risco, dados_alavancagem, dados_tatica
        )
        
        # Salvar no PostgreSQL
        success = save_dashboard(dashboard_data)
        if not success:
            raise Exception("Falha ao salvar Dashboard")
        
        return {
            "status": "success",
            "versao": "v1.5",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Dash-main processado e gravado",
            "camadas_processadas": {
                "mercado": "✅ real",
                "risco": "✅ real", 
                "alavancagem": "✅ real",
                "estrategia": "✅ real"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro processar Dash-main: {str(e)}")
        return {
            "status": "error",
            "versao": "1.5",
            "timestamp": datetime.utcnow().isoformat(),
            "erro": str(e),
            "message": "Falha processar Dash-main"
        }

def obter_dash_main() -> dict:
    """Dashboard - GET: Recupera último processado"""
    try:
        logger.info("🔍 Obtendo Dash-main")
        
        dados = get_latest_dashboard()
        
        if not dados:
            return {
                "status": "error",
                "versao": "1.5", 
                "timestamp": datetime.utcnow().isoformat(),
                "erro": "Nenhum dashboard encontrado",
                "message": "Execute POST primeiro para gerar dados"
            }
        
        response = build_response_format(dados)
        logger.info(f"✅ Dashboard obtido: ID {dados['id']}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Erro obter Dashboard: {str(e)}")
        return {
            "status": "error",
            "versao": "1.5",
            "timestamp": datetime.utcnow().isoformat(),
            "erro": str(e),
            "message": "Falha obter Dashboard"
        }

def _executar_camada_risco() -> dict:
    """Executa Camada 2: Análise de Risco"""
    try:
        logger.info("🛡️ Executando Camada 2: Análise Risco...")
        
        resultado = riscos.calcular_score()
        
        return {
            "score": resultado["score_consolidado_100"],
            "classificacao": resultado["classificacao_consolidada"],
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
            "versao": "1.5",
            "ultimo_registro": {
                "id": ultimo["id"] if ultimo else None,
                "created_at": ultimo["created_at"].isoformat() if ultimo else None,
                "tem_dados": ultimo is not None
            },
            "implementacao": {
                "camada_1_mercado": "✅",
                "camada_2_risco": "✅", 
                "camada_3_alavancagem": "✅",
                "camada_4_tatica": "✅"
            },
        }
        
    except Exception as e:
        return {
            "status": "error",
            "erro": str(e),
            "versao": "1.5"
        }