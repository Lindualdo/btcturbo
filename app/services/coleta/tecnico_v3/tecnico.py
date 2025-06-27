# app/services/coleta/tecnico.py - ATUALIZADO para v3.0

from datetime import datetime
import logging
from app.services.utils.helpers.tradingview.ema_calculator import get_complete_ema_analysis
from app.services.scores.tecnico_v3.utils.score_compositor import calcular_score_tecnico_v3
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
            
            # Scores v3.0 (compatibilidade)
            "score_consolidado_1w": resultado_v3["timeframes"]["semanal"]["score_consolidado"],
            "score_consolidado_1d": resultado_v3["timeframes"]["diario"]["score_consolidado"],
            "score_final_ponderado": resultado_v3["score_final"],
            
            # Campos v3.0 auditoria
            "score_alinhamento_v3_1w": resultado_v3["timeframes"]["semanal"]["alinhamento"]["score"],
            "score_expansao_v3_1w": resultado_v3["timeframes"]["semanal"]["expansao"]["score"],
            "score_alinhamento_v3_1d": resultado_v3["timeframes"]["diario"]["alinhamento"]["score"],
            "score_expansao_v3_1d": resultado_v3["timeframes"]["diario"]["expansao"]["score"],
            "score_tecnico_v3_final": resultado_v3["score_final"],
            
            # JSON gerencial v3.1 (usar campo existente)
            "distancias_emas_json": {
                "semanal": {
                    "score_alinhamento": resultado_v3["timeframes"]["semanal"]["alinhamento"]["score"],
                    "score_expansao": resultado_v3["timeframes"]["semanal"]["expansao"]["score"],
                    "expansao_total_pct": _extrair_expansao_total(resultado_v3["timeframes"]["semanal"]["expansao"], emas_semanal),
                    "expansao_critica_pct": _extrair_expansao_critica(resultado_v3["timeframes"]["semanal"]["expansao"], emas_semanal),
                    "adjacente_penalidade": _extrair_adjacente_penalidade(resultado_v3["timeframes"]["semanal"]["expansao"])
                },
                "diario": {
                    "score_alinhamento": resultado_v3["timeframes"]["diario"]["alinhamento"]["score"],
                    "score_expansao": resultado_v3["timeframes"]["diario"]["expansao"]["score"],
                    "expansao_total_pct": _extrair_expansao_total(resultado_v3["timeframes"]["diario"]["expansao"], emas_diario),
                    "expansao_critica_pct": _extrair_expansao_critica(resultado_v3["timeframes"]["diario"]["expansao"], emas_diario),
                    "adjacente_penalidade": _extrair_adjacente_penalidade(resultado_v3["timeframes"]["diario"]["expansao"])
                },
                "formulas": {
                    "score_final": "(Alinhamento × 0.5) + (Expansão × 0.5)",
                    "pesos_timeframe": "(Semanal × 0.7) + (Diário × 0.3)",
                    "expansao_total": "(EMA17 / EMA610 - 1) × 100",
                    "expansao_critica": "(EMA17 / EMA144 - 1) × 100",
                    "expansao_score": "100 - (Total×0.4 + Crítica×0.4 + Adjacente×0.2)"
                }
            },
            
            # JSON EMAs (campo legado)
            "distancias_json": {
                "weekly": weekly.get("details", {}).get("position", {}).get("distances", {}),
                "daily": daily.get("details", {}).get("position", {}).get("distances", {}),
                "weights": {"weekly": 0.7, "daily": 0.3}
            },
            
            "versao_calculo": "v3.0",
            "fonte": "tradingview_v3",
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
            "score_final": resultado_v3["score_final"],
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

def _extrair_expansao_total(expansao_data: dict, emas: dict) -> float:
    """Extrai percentual expansão total: (EMA17/EMA610 - 1) × 100"""
    try:
        if emas[610] == 0:
            return 0.0
        return round(((emas[17] / emas[610]) - 1) * 100, 2)
    except:
        return 0.0

def _extrair_expansao_critica(expansao_data: dict, emas: dict) -> float:
    """Extrai percentual expansão crítica: (EMA17/EMA144 - 1) × 100"""
    try:
        if emas[144] == 0:
            return 0.0
        return round(((emas[17] / emas[144]) - 1) * 100, 2)
    except:
        return 0.0

def _extrair_adjacente_penalidade(expansao_data: dict) -> int:
    """Extrai penalidade total adjacente"""
    try:
        return expansao_data.get("componentes", {}).get("expansao_adjacente", {}).get("penalidade", 0)
    except:
        return 0