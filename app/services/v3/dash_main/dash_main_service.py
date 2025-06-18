# app/services/v3/dash_main/dash_main_service.py

import logging
from datetime import datetime
from app.services.v3.analise_mercado import analise_mercado_service
from app.services.scores import riscos
logger = logging.getLogger(__name__)

def processar_dashboard() -> dict:
    """
    Dashboard V3 - 4 Camadas Sequenciais
    
    Status implementação:
    - [✅] Camada 1: Análise Mercado (score + ciclo)  
    - [✅] Camada 2: Análise Risco (health_factor + score)
    - [ ] Camada 3: Análise Alavancagem (limites + status)
    - [ ] Camada 4: Execução Tática (decisão + setup)
    """
    try:
        logger.info("🚀 Processando Dashboard V3 - 2 Camadas")
        
        # CAMADA 1: Análise Mercado
        dados_mercado = analise_mercado_service.executar_analise()
        logger.info(f"✅ Camada 1: Score {dados_mercado['score_consolidado']} - {dados_mercado['classificacao']}")
        
        # CAMADA 2: Análise Risco
        dados_risco = _executar_camada_risco()
        logger.info(f"✅ Camada 2: Score {dados_risco['score']} - {dados_risco['classificacao']}")
        
        # CAMADAS 3-4: Mock
        mock_data = _get_mock_dashboard_data()
        
        # Consolidar dados reais das camadas 1 e 2
        mock_data.update({
            # Camada 1
            "score_mercado": dados_mercado["score_consolidado"],
            "classificacao_mercado": dados_mercado["classificacao"], 
            "ciclo": dados_mercado["ciclo"],
            "mvrv": dados_mercado["blocos"]["ciclo"]["indicadores"]["mvrv"]["valor"],
            "nupl": dados_mercado["blocos"]["ciclo"]["indicadores"]["nupl"]["valor"],
            
            # Camada 2
            "score_risco": dados_risco["score"],
            "classificacao_risco": dados_risco["classificacao"],
            "health_factor": dados_risco["health_factor"],
            "dist_liquidacao": dados_risco["dist_liquidacao"]
        })
        
        # Salvar no banco
        dashboard_id = _save_dashboard_v3(mock_data)
        
        # Retornar JSON compatível
        response = {
            "status": "success", 
            "id": dashboard_id,
            "timestamp": datetime.utcnow().isoformat(),
            "score_consolidado": dados_mercado["score_consolidado"],
            "classificacao": dados_mercado["classificacao"],
            "blocos": dados_mercado["blocos"]
        }
        
        logger.info(f"✅ Dashboard V3 processado: ID {dashboard_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Erro processar Dashboard V3: {str(e)}")
        raise Exception(f"Falha dashboard: {str(e)}")

def _executar_camada_risco() -> dict:
    """Camada 2: consome função existente calcular_score_risco()"""
    try:
        logger.info("🛡️ Executando Camada 2: Análise Risco...")
        
        # Usar função existente
        resultado = riscos.calcular_score() 
        
        if resultado.get("status") != "success":
            error_msg = f"Falha calcular_score_risco: {resultado.get('erro', 'erro desconhecido')}"
            logger.error(f"❌ {error_msg}")
            raise Exception(error_msg)
        
        # Adaptar formato para dashboard
        return {
            "score": resultado["score_consolidado"],
            "classificacao": resultado["classificacao"],
            "health_factor": resultado.get("health_factor", 0),
            "dist_liquidacao": resultado.get("dist_liquidacao", 0),
            "status": "success"
        }
        
    except Exception as e:
        error_msg = f"Erro Camada 2 Risco: {str(e)}"
        logger.error(f"❌ {error_msg}")
        raise Exception(error_msg)

def _get_mock_dashboard_data() -> dict:
    """Mock camadas 3-4 baseado no JSON fornecido"""
    return {
        "btc_price": 104350.29,
        "position_usd": 124987.126836,
        "rsi_diario": 43.8,
        "preco_ema144": 106080.29630039757,
        "ema_distance": -1.29,
        "decisao": "AJUSTAR_ALAVANCAGEM",
        "setup_4h": "PULLBACK_TENDENCIA", 
        "urgencia": "alta",
        "justificativa": "Alavancagem no limite: 2.0x >= 2.0x",
        "alavancagem_atual": 2.04,
        "status_alavancagem": "deve_reduzir",
        "alavancagem_permitida": 2.0,
        "divida_total": 63836.377046,
        "valor_a_reduzir": 2685.63,
        "valor_disponivel": 0.0
    }

def _save_dashboard_v3(data: dict) -> int:
    """Salva dashboard V3 - TODO: PostgreSQL"""
    try:
        logger.info("💾 Salvando Dashboard V3 (MOCK)")
        return 48
        
    except Exception as e:
        logger.error(f"❌ Erro salvar Dashboard V3: {str(e)}")
        raise Exception(f"Falha ao salvar: {str(e)}")

def obter_dashboard() -> dict:
    """Obtém último dashboard V3 processado"""
    try:
        logger.info("🔍 Obtendo Dashboard V3...")
        return processar_dashboard()
        
    except Exception as e:
        logger.error(f"❌ Erro obter Dashboard V3: {str(e)}")
        return {
            "status": "error",
            "erro": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

def debug_mercado() -> dict:
    """Debug apenas camada mercado"""
    return executar_analise()

def debug_dashboard() -> dict:
    """Debug status implementação"""
    return {
        "status": "success",
        "versao": "v3_camada_2_implementada",
        "implementacao": {
            "camada_1_mercado": "✅ IMPLEMENTADA",
            "camada_2_risco": "✅ IMPLEMENTADA", 
            "camada_3_alavancagem": "❌ TODO",
            "camada_4_tatica": "❌ TODO"
        }
    }