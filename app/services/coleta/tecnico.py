# app/services/coleta/tecnico.py

from datetime import datetime
import logging
import json
from app.services.utils.helpers.tradingview.ema_calculator import get_complete_ema_analysis
from app.services.utils.helpers.postgres.indicadores.tecnico_helper import insert_dados_tecnico_completo

logger = logging.getLogger(__name__)

def coletar(forcar_coleta: bool):
    """
    Coleta dados técnicos EMAs via TradingView e grava no PostgreSQL
    """
    try:
        logger.info("🚀 Iniciando coleta técnica EMAs...")
        
        # 1. Obter análise completa EMAs
        logger.info("📊 Calculando EMAs e scores...")
        analysis = get_complete_ema_analysis()
        
        if analysis.get("status") != "success":
            raise Exception(f"Análise EMAs falhou: {analysis.get('error', 'Erro desconhecido')}")
        
        # 2. Extrair dados para PostgreSQL
        weekly = analysis["weekly"]
        daily = analysis["daily"]
        final_weighted = analysis["final_weighted"]
        
        if weekly.get("status") != "success" or daily.get("status") != "success":
            raise Exception("Dados EMAs incompletos")
        
        # 3. Preparar dados para inserção
        dados_para_db = {
            # EMAs Semanal (1W)
            "ema_17_1w": weekly["emas"][17],
            "ema_34_1w": weekly["emas"][34],
            "ema_144_1w": weekly["emas"][144],
            "ema_305_1w": weekly["emas"][305],
            "ema_610_1w": weekly["emas"][610],
            
            # EMAs Diário (1D)
            "ema_17_1d": daily["emas"][17],
            "ema_34_1d": daily["emas"][34],
            "ema_144_1d": daily["emas"][144],
            "ema_305_1d": daily["emas"][305],
            "ema_610_1d": daily["emas"][610],
            
            # Preço atual
            "btc_price_current": weekly["current_price"],  # Usar preço do semanal como referência
            
            # Scores individuais
            "score_1w_ema": weekly["scores"]["alignment"],
            "score_1w_price": weekly["scores"]["position"],
            "score_1d_ema": daily["scores"]["alignment"],
            "score_1d_price": daily["scores"]["position"],
            
            # Scores consolidados
            "score_consolidado_1w": weekly["scores"]["consolidated"],
            "score_consolidado_1d": daily["scores"]["consolidated"],
            "score_final_ponderado": final_weighted["final_score"],
            
            # Distâncias em JSON
            "distancias_json": {
                "weekly": weekly["details"]["position"].get("distances", {}),
                "daily": daily["details"]["position"].get("distances", {}),
                "weights": final_weighted["weights"]
            },
            
            # Metadados
            "fonte": "tvdatafeed_emas",
            "timestamp": datetime.utcnow()
        }
        
        # 4. Gravar no PostgreSQL
        logger.info("💾 Gravando dados no PostgreSQL...")
        sucesso = insert_dados_tecnico_completo(dados_para_db)
        
        if not sucesso:
            raise Exception("Falha ao gravar no PostgreSQL")
        
        # 5. Preparar resposta de sucesso
        return {
            "bloco": "tecnico",
            "status": "sucesso",
            "timestamp": datetime.utcnow().isoformat(),
            },
    except Exception as e:
        logger.error(f"❌ Erro na coleta técnica: {str(e)}")
        return {
            "bloco": "tecnico",
            "status": "erro",
            "timestamp": datetime.utcnow().isoformat(),
            "detalhes": f"Falha na coleta EMAs: {str(e)}",
            "fonte": "tvdatafeed_emas"
        }