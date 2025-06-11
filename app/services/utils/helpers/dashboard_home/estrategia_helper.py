# app/services/utils/helpers/dashboard_home/estrategia_helper.py

import logging
from app.services.utils.helpers.analise.matriz_cenarios_completos_helper import avaliar_cenario_completo
from app.services.utils.helpers.analise.matriz_tatica_helper import encontrar_acao_tatica
from app.services.utils.helpers.analise.ema144_live_helper import obter_ema144_distance_atualizada
from app.services.utils.helpers.rsi_helper import obter_rsi_diario
from app.services.utils.helpers.tradingview_helper import fetch_ohlc_data, calculate_ema
from tvDatafeed import Interval

logger = logging.getLogger(__name__)

def get_estrategia_data(dados_dashboard: dict = None) -> dict:
    """
    Coleta dados da estratégia: ação, cenário, justificativa baseado nas matrizes
    
    Args:
        dados_dashboard: Dados dos outros módulos (mercado, risco, alavancagem)
    
    Returns:
        dict com campos da estratégia ou erro
    """
    try:
        logger.info("🎯 Coletando dados da estratégia...")
        
        # 1. Obter dados técnicos necessários
        ema_distance = obter_ema144_distance_atualizada()
        rsi_diario = obter_rsi_diario()
        ema_valor = _obter_ema144_valor()
        
        # 2. Extrair dados dos outros módulos do dashboard
        if not dados_dashboard:
            raise Exception("Dados do dashboard são obrigatórios")
        
        mercado_data = dados_dashboard.get("mercado", {})
        risco_data = dados_dashboard.get("risco", {})
        
        score_mercado = float(mercado_data.get("campos", {}).get("score_mercado", 0))
        score_risco = float(risco_data.get("campos", {}).get("score_risco", 0))
        mvrv_valor = float(mercado_data.get("campos", {}).get("mvrv_valor", 0))
        health_factor = float(risco_data.get("campos", {}).get("health_factor", 0))
        dist_liquidacao = float(risco_data.get("campos", {}).get("dist_liquidacao", 0))
        
        logger.info(f"📊 Dados para estratégia: EMA={ema_distance:+.1f}%, RSI={rsi_diario:.1f}, Mercado={score_mercado:.1f}, Risco={score_risco:.1f}")
        
        # 3. Avaliar cenários completos primeiro
        cenario, motivo_escolha = avaliar_cenario_completo(
            score_mercado=score_mercado,
            score_risco=score_risco,
            mvrv=mvrv_valor,
            ema_distance=ema_distance,
            rsi_diario=rsi_diario,
            dados_extras={
                "health_factor": health_factor,
                "dist_liquidacao": dist_liquidacao,
                "bbw_percentage": 15.0  # Valor padrão
            }
        )
        
        # 4. Processar resultado do cenário
        if cenario["id"] != "indefinido":
            # Cenário específico encontrado
            acao = _mapear_decisao_cenario(cenario["acao"]["decisao"])
            tamanho_percent = cenario["acao"].get("tamanho_percent", 0)
            justificativa = cenario["acao"]["justificativa"]
            urgencia = _determinar_urgencia(cenario)
            matriz_usada = "cenarios_completos"
            cenario_nome = cenario["id"]
            
        else:
            # Fallback: usar matriz básica EMA144 + RSI
            logger.info("📋 Usando matriz básica EMA144 + RSI (fallback)")
            regra_tatica = encontrar_acao_tatica(ema_distance, rsi_diario)
            
            acao = regra_tatica["acao"]
            tamanho_percent = regra_tatica["tamanho"]
            justificativa = regra_tatica["justificativa"]
            urgencia = "baixa"
            matriz_usada = "matriz_basica"
            cenario_nome = "matriz_tatica_basica"
        
        # 5. Determinar urgência se não definida
        if cenario.get("override"):
            urgencia = "critica"
        elif cenario["prioridade"] <= 1:
            urgencia = "alta"
        elif cenario["prioridade"] <= 2:
            urgencia = "media"
        else:
            urgencia = "baixa"
        
        # 6. Campos para PostgreSQL
        campos_estrategia = {
            "acao_estrategia": acao,
            "tamanho_percent_estrategia": tamanho_percent,
            "cenario_estrategia": cenario_nome,
            "justificativa_estrategia": justificativa,
            "urgencia_estrategia": urgencia,
            "ema_distance": ema_distance,
            "ema_valor": ema_valor,
            "rsi_diario": rsi_diario,
            "matriz_usada": matriz_usada
        }
        
        # 7. JSON para frontend
        json_estrategia = {
            "acao": acao,
            "tamanho_percent": tamanho_percent,
            "cenario": cenario_nome,
            "justificativa": justificativa,
            "urgencia": urgencia,
            "dados_decisao": {
                "ema_distance": ema_distance,
                "ema_valor": ema_valor,
                "rsi_diario": rsi_diario,
                "score_mercado": score_mercado,
                "score_risco": score_risco,
                "mvrv": mvrv_valor,
                "matriz_usada": matriz_usada
            }
        }
        
        logger.info(f"✅ Estratégia: {acao} {tamanho_percent}% - {cenario_nome} ({urgencia})")
        
        return {
            "status": "success",
            "campos": campos_estrategia,
            "json": json_estrategia,
            "modulo": "estrategia",
            "fonte": f"{matriz_usada} + ema144_live + rsi_helper"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na estratégia: {str(e)}")
        return {
            "status": "error",
            "erro": str(e),
            "campos": {
                "acao_estrategia": "ERROR",
                "tamanho_percent_estrategia": 0,
                "cenario_estrategia": "erro",
                "justificativa_estrategia": "Sistema indisponível",
                "urgencia_estrategia": "baixa",
                "ema_distance": 0.0,
                "ema_valor": 0.0,
                "rsi_diario": 0.0,
                "matriz_usada": "erro"
            }
        }

def _obter_ema144_valor() -> float:
    """Obter valor absoluto da EMA144 em dólares"""
    try:
        # Buscar dados do BTC
        df = fetch_ohlc_data(
            symbol="BTCUSDT",
            exchange="BINANCE", 
            interval=Interval.in_daily,
            n_bars=200
        )
        
        # Calcular EMA144
        ema_144 = calculate_ema(df['close'], period=144)
        ema_valor = float(ema_144.iloc[-1])
        
        logger.debug(f"📊 EMA144 valor: ${ema_valor:,.2f}")
        return round(ema_valor, 2)
        
    except Exception as e:
        logger.error(f"❌ Erro obtendo EMA144 valor: {str(e)}")
        return 0.0

def _mapear_decisao_cenario(decisao_cenario: str) -> str:
    """Mapeia decisão do cenário para ação padrão"""
    mapeamento = {
        "ENTRAR": "ADICIONAR",
        "REALIZAR_PARCIAL": "REALIZAR", 
        "REALIZAR_AGRESSIVO": "REALIZAR",
        "ADICIONAR_AGRESSIVO": "ADICIONAR",
        "REDUZIR_DEFENSIVO": "REALIZAR",
        "ACUMULAR_SPOT_APENAS": "ADICIONAR",
        "EMERGENCIA_REDUZIR": "REALIZAR",
        "PREPARAR_BREAKOUT": "HOLD",
        "HOLD_NEUTRO": "HOLD"
    }
    
    return mapeamento.get(decisao_cenario, "HOLD")

def _determinar_urgencia(cenario: dict) -> str:
    """Determina urgência baseada no cenário"""
    if cenario.get("override"):
        return "critica"
    elif cenario["prioridade"] == 0:
        return "critica" 
    elif cenario["prioridade"] == 1:
        return "alta"
    elif cenario["prioridade"] == 2:
        return "media"
    else:
        return "baixa"