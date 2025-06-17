# services/v3/gera_json.py
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_dashboard_json_v3(data: dict) -> dict:
    """
    Gera JSON final compatível com V2
    Estrutura: header, scores, tecnicos, estrategia, alavancagem
    """
    try:
        logger.info("📝 Gerando JSON dashboard V3...")
        
        # Extrair dados das camadas
        mercado = data["mercado"]
        risco = data["risco"]
        alavancagem = data["alavancagem"]
        tatica = data["tatica"]
        
        # Montar JSON compatível V2
        dashboard_json = {
            "header": {
                "status": _determine_status(risco, alavancagem, tatica),
                "btc_price": mercado["btc_price"],
                "alavancagem_atual": alavancagem["alavancagem_atual"]
            },
            "scores": {
                "mvrv": mercado["mvrv_zscore"],
                "risco": risco["score"],
                "mercado": mercado["score"],
                "health_factor": risco["health_factor"]
            },
            "tecnicos": {
                "rsi_diario": mercado["rsi_diario"],
                "ema_distance": mercado["ema_distance"],
                "preco_ema144": mercado["ema144_value"]
            },
            "estrategia": {
                "ciclo": mercado["ciclo"],
                "decisao": tatica["decisao"],
                "setup_4h": tatica["setup"],
                "urgencia": tatica["urgencia"],
                "justificativa": tatica["justificativa"]
            },
            "alavancagem": {
                "atual": alavancagem["alavancagem_atual"],
                "permitida": alavancagem["limite_max"],
                "dist_liquidacao": alavancagem["dist_liquidacao_percent"],
                "valor_disponivel": alavancagem["capital_livre_valor"]
            }
        }
        
        logger.info("✅ JSON V3 gerado - compatível V2")
        return dashboard_json
        
    except Exception as e:
        logger.error(f"❌ Erro gerar JSON: {str(e)}")
        raise Exception(f"Falha ao gerar JSON: {str(e)}")

def _determine_status(risco: dict, alavancagem: dict, tatica: dict) -> str:
    """Determina status operacional baseado nas condições"""
    
    # Verificações de segurança
    if risco["health_factor"] < 1.2:
        return "risco_critico"
    
    if risco["score"] < 40:
        return "risco_alto"
    
    if alavancagem["capital_livre_percent"] < 5:
        return "capital_baixo"
    
    if alavancagem["alavancagem_atual"] >= alavancagem["limite_max"]:
        return "ajustar_posicao"
    
    # Status operacional normal
    if tatica["decisao"] in ["COMPRAR", "ADICIONAR"]:
        return "pode_aumentar"
    elif tatica["decisao"] in ["REALIZAR", "REDUZIR"]:
        return "realizar_lucros"
    else:
        return "aguardar_setup"