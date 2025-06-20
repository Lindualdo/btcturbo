# app/services/coleta/tecnico.py

from datetime import datetime
import logging
import json
from app.services.utils.helpers.tradingview.ema_calculator import get_complete_ema_analysis
from app.services.utils.helpers.postgres.tecnico_helper import insert_dados_tecnico_completo

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
            "detalhes": "Dados EMAs coletados via TradingView",
            "dados_coletados": {
                "timeframes": ["1W", "1D"],
                "emas_calculadas": list(weekly["emas"].keys()),
                "btc_price": f"${weekly['current_price']:,.2f}",
                "scores": {
                    "semanal": {
                        "alinhamento": weekly["scores"]["alignment"],
                        "posicao": weekly["scores"]["position"],
                        "consolidado": weekly["scores"]["consolidated"]
                    },
                    "diario": {
                        "alinhamento": daily["scores"]["alignment"],
                        "posicao": daily["scores"]["position"],
                        "consolidado": daily["scores"]["consolidated"]
                    },
                    "final_ponderado": final_weighted["final_score"]
                }
            },
            "alertas": generate_alerts(weekly, daily, final_weighted),
            "fonte": "tvdatafeed_emas"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na coleta técnica: {str(e)}")
        return {
            "bloco": "tecnico",
            "status": "erro",
            "timestamp": datetime.utcnow().isoformat(),
            "detalhes": f"Falha na coleta EMAs: {str(e)}",
            "fonte": "tvdatafeed_emas"
        }

def generate_alerts(weekly_data: dict, daily_data: dict, final_weighted: dict) -> list:
    """Gera alertas baseados nos dados EMAs coletados"""
    alerts = []
    
    try:
        # Alertas de score baixo
        final_score = final_weighted.get("final_score", 0)
        if final_score < 4:
            alerts.append(f"🚨 Score técnico baixo: {final_score:.1f}/10 - Considerar redução")
        elif final_score < 6:
            alerts.append(f"⚠️ Score técnico neutro: {final_score:.1f}/10 - Cautela")
        
        # Alertas de divergência entre timeframes
        weekly_score = weekly_data.get("scores", {}).get("consolidated", 0)
        daily_score = daily_data.get("scores", {}).get("consolidated", 0)
        
        divergence = abs(weekly_score - daily_score)
        if divergence > 3:
            alerts.append(f"📊 Divergência entre timeframes: {divergence:.1f} pontos")
        
        # Alertas de distância extrema
        weekly_distances = weekly_data.get("details", {}).get("position", {}).get("distances", {})
        for ema, dist_str in weekly_distances.items():
            if "%" in dist_str:
                dist_pct = float(dist_str.replace("%", "").replace("+", ""))
                if dist_pct > 10:
                    alerts.append(f"🔥 Preço muito esticado: {dist_pct:+.1f}% da {ema.upper()}")
                elif dist_pct < -5:
                    alerts.append(f"📉 Rompimento potencial: {dist_pct:+.1f}% da {ema.upper()}")
        
        # Alerta de alinhamento quebrado
        weekly_alignment = weekly_data.get("scores", {}).get("alignment", 10)
        if weekly_alignment < 6:
            alerts.append("💔 Alinhamento EMAs semanal enfraquecendo")
        
        return alerts
        
    except Exception as e:
        logger.error(f"❌ Erro gerando alertas: {str(e)}")
        return ["⚠️ Erro ao gerar alertas técnicos"]