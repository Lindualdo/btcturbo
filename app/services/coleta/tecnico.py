# app/services/coleta/tecnico.py - EXPANDIDO COM BBW

from datetime import datetime
import logging
import json
from tvDatafeed import Interval
from app.services.utils.helpers.ema_calculator import get_complete_ema_analysis
from app.services.utils.helpers.bbw_calculator import (
    calculate_bollinger_bands, calculate_bbw_percentage, calculate_bbw_score
)
from app.services.utils.helpers.postgres.tecnico_helper import insert_dados_tecnico_completo

logger = logging.getLogger(__name__)

def coletar(forcar_coleta: bool):
    """
    Coleta dados técnicos EMAs + BBW via TradingView e grava no PostgreSQL
    """
    try:
        logger.info("🚀 Iniciando coleta técnica EMAs + BBW...")
        
        # 1. Obter análise completa EMAs (existente)
        logger.info("📊 Calculando EMAs e scores...")
        analysis = get_complete_ema_analysis()
        
        if analysis.get("status") != "success":
            raise Exception(f"Análise EMAs falhou: {analysis.get('error', 'Erro desconhecido')}")
        
        # 2. NOVO: Obter dados para BBW
        logger.info("📈 Calculando Bollinger Band Width...")
        bbw_data = get_bbw_data()
        
        # 3. Extrair dados EMAs para PostgreSQL (existente)
        weekly = analysis["weekly"]
        daily = analysis["daily"]
        final_weighted = analysis["final_weighted"]
        
        if weekly.get("status") != "success" or daily.get("status") != "success":
            raise Exception("Dados EMAs incompletos")
        
        # 4. NOVO: Calcular score final do bloco técnico
        score_emas_consolidado = final_weighted["final_score"]
        score_bbw = bbw_data["score"]
        score_bloco_final = (score_emas_consolidado * 0.7) + (score_bbw * 0.3)
        
        # 5. Preparar dados completos para inserção
        dados_para_db = {
            # EMAs Semanal (1W) - existente
            "ema_17_1w": weekly["emas"][17],
            "ema_34_1w": weekly["emas"][34],
            "ema_144_1w": weekly["emas"][144],
            "ema_305_1w": weekly["emas"][305],
            "ema_610_1w": weekly["emas"][610],
            
            # EMAs Diário (1D) - existente
            "ema_17_1d": daily["emas"][17],
            "ema_34_1d": daily["emas"][34],
            "ema_144_1d": daily["emas"][144],
            "ema_305_1d": daily["emas"][305],
            "ema_610_1d": daily["emas"][610],
            
            # Preço atual - existente
            "btc_price_current": weekly["current_price"],
            
            # Scores EMAs individuais - existente
            "score_1w_ema": weekly["scores"]["alignment"],
            "score_1w_price": weekly["scores"]["position"],
            "score_1d_ema": daily["scores"]["alignment"],
            "score_1d_price": daily["scores"]["position"],
            
            # Scores EMAs consolidados - existente
            "score_consolidado_1w": weekly["scores"]["consolidated"],
            "score_consolidado_1d": daily["scores"]["consolidated"],
            "score_final_ponderado": score_emas_consolidado,
            
            # NOVO: BBW
            "bbw_percentage": bbw_data["bbw_percentage"],
            "score_bbw": score_bbw,
            
            # NOVO: Score final do bloco
            "score_bloco_final": score_bloco_final,
            
            # Distâncias em JSON - existente + BBW
            "distancias_json": {
                "weekly": weekly["details"]["position"].get("distances", {}),
                "daily": daily["details"]["position"].get("distances", {}),
                "weights": final_weighted["weights"],
                "bbw": bbw_data  # Adicionar dados BBW
            },
            
            # Metadados - existente
            "fonte": "tvdatafeed_emas_bbw",
            "timestamp": datetime.utcnow()
        }
        
        # 6. Gravar no PostgreSQL
        logger.info("💾 Gravando dados no PostgreSQL...")
        sucesso = insert_dados_tecnico_completo(dados_para_db)
        
        if not sucesso:
            raise Exception("Falha ao gravar no PostgreSQL")
        
        # 7. Preparar resposta de sucesso
        return {
            "bloco": "tecnico",
            "status": "sucesso",
            "timestamp": datetime.utcnow().isoformat(),
            "detalhes": "Dados EMAs + BBW coletados via TradingView",
            "dados_coletados": {
                "timeframes": ["1W", "1D"],
                "emas_calculadas": list(weekly["emas"].keys()),
                "btc_price": f"${weekly['current_price']:,.2f}",
                "scores_emas": {
                    "semanal": weekly["scores"]["consolidated"],
                    "diario": daily["scores"]["consolidated"],
                    "final_ponderado": score_emas_consolidado
                },
                "bbw": {
                    "percentage": f"{bbw_data['bbw_percentage']:.2f}%",
                    "score": score_bbw,
                    "interpretacao": bbw_data["interpretacao"]
                },
                "score_bloco_final": score_bloco_final
            },
            "alertas": generate_alerts_with_bbw(weekly, daily, final_weighted, bbw_data),
            "fonte": "tvdatafeed_emas_bbw"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na coleta técnica: {str(e)}")
        return {
            "bloco": "tecnico",
            "status": "erro",
            "timestamp": datetime.utcnow().isoformat(),
            "detalhes": f"Falha na coleta EMAs + BBW: {str(e)}",
            "fonte": "tvdatafeed_emas_bbw"
        }

def get_bbw_data():
    """
    Busca dados para calcular BBW via TradingView
    """
    try:
        from app.services.utils.helpers.ema_calculator import EMACalculator
        
        calculator = EMACalculator()
        tv = calculator.get_tv_session()
        
        # Buscar dados diários (20 períodos para Bollinger Bands)
        logger.info("📊 Buscando dados para BBW (20 períodos)...")
        df = tv.get_hist(
            symbol="BTCUSDT",
            exchange="BINANCE", 
            interval=Interval.in_daily,
            n_bars=30  # 30 barras para garantir 20 períodos
        )
        
        if df is None or df.empty:
            raise Exception("Dados TradingView indisponíveis para BBW")
        
        # Calcular Bollinger Bands
        upper_band, lower_band, middle_band = calculate_bollinger_bands(df['close'])
        
        # Calcular BBW%
        bbw_percentage = calculate_bbw_percentage(upper_band, lower_band, middle_band)
        
        # Calcular score BBW
        score_bbw = calculate_bbw_score(bbw_percentage)
        
        # Interpretação
        from app.services.utils.helpers.bbw_calculator import get_bbw_interpretation
        interpretacao = get_bbw_interpretation(bbw_percentage)
        
        return {
            "bbw_percentage": bbw_percentage,
            "score": score_bbw,
            "bands": {
                "upper": upper_band,
                "lower": lower_band,
                "middle": middle_band
            },
            "interpretacao": interpretacao,
            "periodo": 20,
            "std_dev": 2.0
        }
        
    except Exception as e:
        logger.error(f"❌ Erro calculando BBW: {str(e)}")
        # Fallback: BBW neutro
        return {
            "bbw_percentage": 15.0,  # Valor neutro
            "score": 5.0,           # Score neutro
            "bands": None,
            "interpretacao": {"status": "Erro no cálculo"},
            "erro": str(e)
        }

def generate_alerts_with_bbw(weekly_data: dict, daily_data: dict, final_weighted: dict, bbw_data: dict) -> list:
    """
    Gera alertas incluindo BBW
    """
    alerts = []
    
    try:
        # Alertas EMAs existentes
        final_score = final_weighted.get("final_score", 0)
        if final_score < 4:
            alerts.append(f"🚨 Score EMAs baixo: {final_score:.1f}/10 - Reduzir alavancagem")
        elif final_score < 6:
            alerts.append(f"⚠️ Score EMAs neutro: {final_score:.1f}/10 - Cautela recomendada")
        
        # NOVO: Alertas BBW
        bbw_percentage = bbw_data.get("bbw_percentage", 15)
        
        if bbw_percentage < 5:
            alerts.append(f"🎯 BBW extremamente baixo: {bbw_percentage:.1f}% - Breakout iminente")
        elif bbw_percentage < 8:
            alerts.append(f"📈 BBW baixo: {bbw_percentage:.1f}% - Preparar para movimento")
        elif bbw_percentage > 30:
            alerts.append(f"🌪️ BBW alto: {bbw_percentage:.1f}% - Volatilidade extrema")
        elif bbw_percentage > 25:
            alerts.append(f"⚡ BBW elevado: {bbw_percentage:.1f}% - Mercado agitado")
        
        # Divergência EMAs vs BBW
        score_emas = final_weighted.get("final_score", 5)
        score_bbw = bbw_data.get("score", 5)
        divergence = abs(score_emas - score_bbw)
        
        if divergence > 3:
            alerts.append(f"🔄 Divergência EMAs/BBW: {divergence:.1f} pontos - Analisar conflito")
        
        return alerts
        
    except Exception as e:
        logger.error(f"❌ Erro gerando alertas: {str(e)}")
        return [f"⚠️ Erro ao gerar alertas: {str(e)}"]