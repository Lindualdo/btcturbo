# app/services/coleta/tecnico_v3/tecnico.py - VERSÃO SIMPLIFICADA

from datetime import datetime
import logging
from app.services.utils.helpers.tradingview.ema_calculator import get_complete_ema_analysis
from .utils.score_compositor import calcular_score_tecnico_v3
from app.services.utils.helpers.postgres.indicadores.tecnico_v3_helper import insert_dados_tecnico

logger = logging.getLogger(__name__)

def coletar(forcar_coleta: bool):
    """Coleta dados técnicos EMAs via TradingView e calcula score v3.0 - VERSÃO SIMPLIFICADA"""
    try:
        logger.info("🚀 Iniciando coleta técnica v3.0 SIMPLIFICADA...")
        
        # 1. Buscar EMAs do TradingView
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
        
        # 4. Preparar dados ESSENCIAIS para gravação - SEM CAMPOS COMPLEXOS
        dados_para_db = {
            # === EMAs SEMANAL (5 campos) ===
            "ema_17_1w": emas_semanal[17],
            "ema_34_1w": emas_semanal[34], 
            "ema_144_1w": emas_semanal[144],
            "ema_305_1w": emas_semanal[305],
            "ema_610_1w": emas_semanal[610],
            
            # === EMAs DIÁRIO (5 campos) ===
            "ema_17_1d": emas_diario[17],
            "ema_34_1d": emas_diario[34],
            "ema_144_1d": emas_diario[144], 
            "ema_305_1d": emas_diario[305],
            "ema_610_1d": emas_diario[610],
            
            # === PREÇO ATUAL (1 campo) ===
            "btc_price_current": weekly["current_price"],
            
            # === SCORES PRINCIPAIS (3 campos) ===
            "score_consolidado_1w": resultado_v3["timeframes"]["semanal"]["score_consolidado"],
            "score_consolidado_1d": resultado_v3["timeframes"]["diario"]["score_consolidado"],
            "score_final_ponderado": resultado_v3["score_final"],
            
            # === METADADOS BÁSICOS (2 campos) ===
            "fonte": "tradingview_v3",
            "timestamp": datetime.utcnow()
        }
        
        # 5. Gravar no banco - FUNÇÃO SIMPLIFICADA
        logger.info("💾 Gravando dados v3.0 SIMPLIFICADOS...")
        sucesso = insert_dados_tecnico(dados_para_db)
        
        if not sucesso:
            raise Exception("Falha ao gravar no banco")
        
        logger.info(f"✅ Coleta v3.0 SIMPLIFICADA concluída: score={resultado_v3['score_final']}")
        
        # 6. Resposta de sucesso
        return {
            "status": "success",
            "bloco": "tecnico",
            "versao": "v3.0_simplificada",
            "score_final": resultado_v3["score_final"],
            "timestamp": dados_para_db["timestamp"],
            "fonte": "tradingview_v3",
            "campos_gravados": {
                "emas_semanal": 5,
                "emas_diario": 5,
                "preco_atual": 1,
                "scores_principais": 3,
                "metadados": 2,
                "total": 16
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro coleta v3.0 SIMPLIFICADA: {str(e)}")
        return {
            "status": "error",
            "bloco": "tecnico", 
            "erro": str(e),
            "timestamp": datetime.utcnow(),
            "versao": "v3.0_simplificada"
        }