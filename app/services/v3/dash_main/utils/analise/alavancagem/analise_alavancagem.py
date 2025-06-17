# services/v3/utils/analise/alavancagem/analise_alavancagem.py
import logging
from datetime import datetime
from .matriz_alavancagem import calcular_limite_alavancagem
from app.services.utils.helpers.tradingview.rsi_helper import obter_rsi_mensal
from app.services.utils.helpers.postgres.aave_helper import get_current_leverage_data

logger = logging.getLogger(__name__)

def executar_analise_alavancagem(mercado_data: dict, risco_data: dict) -> dict:
    """
    Análise de Alavancagem - Camada 3
    Baseado em: Score Mercado + Indicadores Ciclo + IFR Mensal → Limite máximo (3x)
    """
    try:
        logger.info("⚖️ Executando análise de alavancagem...")
        
        # 1. IFR (RSI) Mensal para timing
        rsi_mensal = obter_rsi_mensal()
        
        # 2. Dados atuais de alavancagem
        leverage_data = get_current_leverage_data()
        
        # 3. Calcular limite baseado na matriz
        limite_calculado = calcular_limite_alavancagem(
            score_mercado=mercado_data["score"],
            mvrv_zscore=mercado_data["mvrv_zscore"],
            ciclo_atual=mercado_data["ciclo"],
            rsi_mensal=rsi_mensal,
            health_factor=risco_data["health_factor"]
        )
        
        # 4. Analisar situação atual vs recomendada
        situacao_atual = _analisar_situacao_atual(leverage_data, limite_calculado)
        
        # 5. Calcular métricas de segurança
        metricas_seguranca = _calcular_metricas_seguranca(leverage_data, limite_calculado)
        
        resultado = {
            "limite_max": limite_calculado["limite_alavancagem"],
            "alavancagem_atual": leverage_data["alavancagem_atual"],
            "pode_aumentar": situacao_atual["pode_aumentar"],
            "margem_disponivel": situacao_atual["margem_disponivel"],
            
            # Capital e liquidação
            "capital_livre_valor": leverage_data["capital_livre_valor"],
            "capital_livre_percent": leverage_data["capital_livre_percent"],
            "dist_liquidacao_percent": metricas_seguranca["dist_liquidacao_percent"],
            "preco_liquidacao": metricas_seguranca["preco_liquidacao"],
            
            # Detalhamento da análise
            "justificativa_limite": limite_calculado["justificativa"],
            "fatores_considerados": {
                "score_mercado": mercado_data["score"],
                "ciclo": mercado_data["ciclo"],
                "mvrv_zscore": mercado_data["mvrv_zscore"],
                "rsi_mensal": rsi_mensal,
                "health_factor": risco_data["health_factor"]
            },
            
            # Recomendações
            "acao_recomendada": situacao_atual["acao_recomendada"],
            "ajuste_necessario": situacao_atual["ajuste_necessario"],
            
            # Metadados
            "timestamp": datetime.utcnow().isoformat(),
            "fonte": "matriz_alavancagem + aave_data",
            "status": "success"
        }
        
        logger.info(f"✅ Alavancagem: Limite {limite_calculado['limite_alavancagem']}x - Atual {leverage_data['alavancagem_atual']}x")
        return resultado
        
    except Exception as e:
        logger.error(f"❌ Erro análise alavancagem: {str(e)}")
        # Retornar dados conservadores em caso de erro
        return {
            "limite_max": 1.5,
            "alavancagem_atual": 1.0,
            "pode_aumentar": False,
            "margem_disponivel": 0.5,
            "capital_livre_valor": 1000.0,
            "capital_livre_percent": 10.0,
            "dist_liquidacao_percent": 50.0,
            "preco_liquidacao": 70000.0,
            "justificativa_limite": "Limite conservador devido a erro no sistema",
            "fatores_considerados": {},
            "acao_recomendada": "MONITORAR",
            "ajuste_necessario": False,
            "timestamp": datetime.utcnow().isoformat(),
            "fonte": "mock_dados_conservador",
            "status": "error",
            "erro": str(e)
        }

def _analisar_situacao_atual(leverage_data: dict, limite_calculado: dict) -> dict:
    """
    Analisa situação atual vs limite recomendado
    """
    atual = leverage_data["alavancagem_atual"]
    limite = limite_calculado["limite_alavancagem"]
    
    # Margem disponível para aumento
    margem_disponivel = max(0, limite - atual)
    
    # Pode aumentar alavancagem?
    pode_aumentar = margem_disponivel > 0.1  # Pelo menos 0.1x de margem
    
    # Determinar ação recomendada
    if atual > limite:
        acao = "REDUZIR_ALAVANCAGEM"
        ajuste_necessario = True
    elif atual < (limite - 0.5):
        acao = "PODE_AUMENTAR"
        ajuste_necessario = False
    else:
        acao = "MANTER_ATUAL"
        ajuste_necessario = False
    
    return {
        "pode_aumentar": pode_aumentar,
        "margem_disponivel": round(margem_disponivel, 2),
        "acao_recomendada": acao,
        "ajuste_necessario": ajuste_necessario,
        "utilizacao_percent": round((atual / limite) * 100, 1) if limite > 0 else 0
    }

def _calcular_metricas_seguranca(leverage_data: dict, limite_calculado: dict) -> dict:
    """
    Calcula métricas de segurança da posição alavancada
    """
    try:
        # Dados necessários
        btc_price_atual = leverage_data.get("btc_price_atual", 105000)
        liquidation_price = leverage_data.get("liquidation_price", 70000)
        
        # Distância até liquidação
        if liquidation_price > 0:
            dist_liquidacao_percent = ((btc_price_atual - liquidation_price) / btc_price_atual) * 100
        else:
            dist_liquidacao_percent = 50.0  # Default seguro
        
        return {
            "dist_liquidacao_percent": round(dist_liquidacao_percent, 2),
            "preco_liquidacao": liquidation_price,
            "margem_seguranca": "ALTA" if dist_liquidacao_percent > 40 else "MEDIA" if dist_liquidacao_percent > 25 else "BAIXA"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro calcular métricas segurança: {str(e)}")
        return {
            "dist_liquidacao_percent": 30.0,
            "preco_liquidacao": 70000.0,
            "margem_seguranca": "MEDIA"
        }