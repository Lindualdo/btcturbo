# app/services/coleta/tecnico.py - ATUALIZADO para v3.0

from datetime import datetime
import logging
from app.services.utils.helpers.tradingview.ema_calculator import get_complete_ema_analysis
from .utils.score_compositor import calcular_score_tecnico_v3
from app.services.utils.helpers.postgres.indicadores.tecnico_v3_helper import insert_dados_tecnico

logger = logging.getLogger(__name__)

def coletar(forcar_coleta: bool):
    """Coleta dados técnicos EMAs via TradingView e calcula score v3.0"""
    try:
        logger.info("🚀 Iniciando coleta técnica v3.0...")
        
        # 1. Buscar EMAs do TradingView (mesmo helper atual)
        logger.info("📊 Buscando EMAs TradingView...")
        analysis = get_complete_ema_analysis()
        
        if analysis.get("status") != "success":
            raise Exception(f"TradingView falhou: {analysis.get('error')}")
        
        # 2. Extrair EMAs por timeframe
        weekly = analysis["weekly"]
        daily = analysis["daily"]
        
        if weekly.get("status") != "success" or daily.get("status") != "success":
            raise Exception("EMAs incompletas")
        
        emas_semanal = weekly["emas"]  # {17: valor, 34: valor, ...}
        emas_diario = daily["emas"]
        
        # 3. Calcular scores v3.0
        logger.info("🔄 Calculando scores v3.0...")
        resultado_v3 = calcular_score_tecnico_v3(emas_semanal, emas_diario)
        
        if resultado_v3["status"] != "success":
            raise Exception(f"Cálculo v3.0 falhou: {resultado_v3.get('erro')}")
        
        # 4. Preparar dados para gravação
        dados_para_db = {
            # EMAs
            "ema_17_1w": emas_semanal[17],
            "ema_34_1w": emas_semanal[34], 
            "ema_144_1w": emas_semanal[144],
            "ema_305_1w": emas_semanal[305],
            "ema_610_1w": emas_semanal[610],
            "ema_17_1d": emas_diario[17],
            "ema_34_1d": emas_diario[34],
            "ema_144_1d": emas_diario[144], 
            "ema_305_1d": emas_diario[305],
            "ema_610_1d": emas_diario[610],
            "btc_price_current": weekly["current_price"],
            
            # Scores Alinhamento
            "score_consolidado_1w": resultado_v3["score_consolidado_1w"],
            "score_consolidado_1d": resultado_v3["score_consolidado_1d"],
            "score_consolidado": resultado_v3["score_consolidado"],
            "classificacao_consolidada": resultado_v3["classificacao_consolidada"],
            "timestamp": datetime.utcnow()
        }
        
        # 5. Gravar no banco
        logger.info("💾 Gravando dados v3.0...")
        sucesso = insert_dados_tecnico(dados_para_db)
        
        if not sucesso:
            raise Exception("Falha ao gravar no banco")
        
        logger.info(f"✅ Coleta v3.0 concluída: score={resultado_v3['score_final']}")
        
        return {
            "status": "success",
            "bloco": "tecnico",
            "versao": "v3.0",
            "score_final": resultado_v3["score_consolidado"],
            "timestamp": dados_para_db["timestamp"],
            "fonte": "tradingview_v3"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro coleta v3.0: {str(e)}")
        return {
            "status": "error",
            "bloco": "tecnico", 
            "erro": str(e),
            "timestamp": datetime.utcnow()
        }