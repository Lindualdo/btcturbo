# app/services/coleta/tecnico.py - ATUALIZADO para v3.0

from datetime import datetime
from typing import Dict
import logging
from app.services.utils.helpers.tradingview.ema_calculator import get_complete_ema_analysis
from .utils.ema_score_calculator import calculate_ema_score
from app.services.utils.helpers.postgres.tendencia import ema_tendencia_helper

logger = logging.getLogger(__name__)

def calcular_score():
    
    try:
        """Coleta dados técnicos EMAs via TradingView e calcula score """

        logger.info("🚀 Iniciando coleta tendencias...")
        
        # 1. Buscar EMAs do TradingView (mesmo helper atual)
        logger.info("📊 Buscando EMAs TradingView...")
        analysis = get_complete_ema_analysis()
        
        if analysis.get("status") != "success":
            raise Exception(f"TradingView falhou: {analysis.get('error')}")
        
        # 2. Extrair EMAs por timeframe
        weekly = analysis["weekly"]
        
        if weekly.get("status") != "success" :
            raise Exception("EMAs incompletas")
        
        emas_semanal = weekly["emas"]  
        
        # 3. Calcular scores
        logger.info("🔄 Calculando scores tendencia")
        btc_price = float(weekly["current_price"])

        resultado = calculate_ema_score(btc_price, emas_semanal )
        
        if resultado["status"] != "success":
            raise Exception(f"Cálculo v3.0 falhou: {resultado.get('erro')}")
        
        # 4. Preparar dados para gravação
        dados_para_db = {
            "emas_json":{
                "ema_10_1w": emas_semanal[10],
                "ema_20_1w": emas_semanal[20], 
                "ema_50_1w": emas_semanal[50],
                "ema_100_1w": emas_semanal[100],
                "ema_200_1w": emas_semanal[200],
                "btc_price_current": btc_price
            },
            
            # Ema score
            "score_emas": resultado["score"],
            "classificacao_emas": resultado["classificacao"],
            "timestamp": datetime.utcnow().isoformat() 
        }
        
        # 5. Gravar no banco
        logger.info("💾 Gravando dados score emas - tendencias...")
        sucesso = ema_tendencia_helper.inserir(dados_para_db)
        
        if not sucesso:
            raise Exception("Falha ao gravar score emas no banco")
        
        logger.info(f"✅ Score tendencia gravado: score={resultado['score']}")
        
        return {
            "status": "success",
            "fonte": "tradingview",
            "dados": dados_para_db
        }
        
    except Exception as e:
        logger.error(f"❌ Erro coleta v3.0: {str(e)}")
        return {
            "status": "error",
            "score": "emas_score", 
            "erro": str(e),
            "timestamp": datetime.utcnow()
        }