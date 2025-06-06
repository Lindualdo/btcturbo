# app/routers/analise_alavancagem.py

from fastapi import APIRouter
from datetime import datetime
from app.services.scores import ciclos
import logging

router = APIRouter()

# Tabela MVRV × RSI conforme especificação v5.0
TABELA_ALAVANCAGEM = [
    {"mvrv_min": 0.0, "mvrv_max": 1.0, "rsi_min": 0, "rsi_max": 30, "fase": "Bottom/Capitulação", "max_leverage": 3.0, "stop_loss": 15},
    {"mvrv_min": 1.0, "mvrv_max": 2.0, "rsi_min": 30, "rsi_max": 50, "fase": "Acumulação", "max_leverage": 2.5, "stop_loss": 12},
    {"mvrv_min": 2.0, "mvrv_max": 3.0, "rsi_min": 50, "rsi_max": 70, "fase": "Bull Médio", "max_leverage": 2.0, "stop_loss": 10},
    {"mvrv_min": 3.0, "mvrv_max": 999, "rsi_min": 70, "rsi_max": 100, "fase": "Euforia/Topo", "max_leverage": 1.5, "stop_loss": 8},
]

def obter_mvrv_do_ciclo():
    """Busca MVRV Z-Score do bloco ciclos"""
    try:
        dados_ciclos = ciclos.calcular_score()
        if dados_ciclos.get("status") == "success":
            indicadores = dados_ciclos.get("indicadores", {})
            mvrv_valor = indicadores.get("MVRV_Z", {}).get("valor", 0)
            return float(mvrv_valor) if mvrv_valor else 0.0
        return 0.0
    except Exception as e:
        logging.error(f"❌ Erro obtendo MVRV: {str(e)}")
        return 0.0

def obter_rsi_mensal():
    """
    TODO: Implementar busca de RSI Mensal
    Por enquanto, usar fallback baseado em MVRV
    """
    # Fallback: estimar RSI baseado em MVRV
    mvrv = obter_mvrv_do_ciclo()
    
    if mvrv < 1.0:
        return 25  # Oversold extremo
    elif mvrv < 2.0:
        return 40  # Oversold
    elif mvrv < 3.0:
        return 60  # Neutro alto
    else:
        return 75  # Overbought

def encontrar_parametros_alavancagem(mvrv: float, rsi_mensal: float) -> dict:
    """Encontra parâmetros na tabela MVRV × RSI"""
    
    for regra in TABELA_ALAVANCAGEM:
        mvrv_ok = regra["mvrv_min"] <= mvrv < regra["mvrv_max"]
        rsi_ok = regra["rsi_min"] <= rsi_mensal <= regra["rsi_max"]
        
        if mvrv_ok and rsi_ok:
            return regra
    
    # Fallback: última regra (mais conservadora)
    return TABELA_ALAVANCAGEM[-1]

def calcular_score_alavancagem(max_leverage: float) -> float:
    """Converte alavancagem máxima em score 0-100"""
    # Quanto maior a alavancagem permitida, maior o score
    if max_leverage >= 3.0:
        return 90  # Ótima oportunidade
    elif max_leverage >= 2.5:
        return 75  # Boa oportunidade
    elif max_leverage >= 2.0:
        return 60  # Oportunidade moderada
    elif max_leverage >= 1.5:
        return 40  # Oportunidade limitada
    else:
        return 20  # Evitar alavancagem

def classificar_oportunidade(score: float) -> str:
    """Classifica oportunidade de alavancagem"""
    if score >= 80:
        return "excelente"
    elif score >= 60:
        return "boa"
    elif score >= 40:
        return "moderada"
    else:
        return "limitada"

def obter_acao_recomendada(max_leverage: float, fase: str) -> str:
    """Determina ação baseada na alavancagem máxima"""
    if max_leverage >= 3.0:
        return f"Aproveitar {fase.lower()} - usar até {max_leverage}x com cautela"
    elif max_leverage >= 2.0:
        return f"Posição moderada em {fase.lower()} - máximo {max_leverage}x"
    elif max_leverage >= 1.5:
        return f"Ser conservador em {fase.lower()} - máximo {max_leverage}x"
    else:
        return f"Evitar alavancagem em {fase.lower()} - apenas spot"

def get_insights_alavancagem(mvrv: float, rsi_mensal: float, fase: str, max_leverage: float) -> list:
    """Gera insights sobre dimensionamento"""
    insights = []
    
    # Insights por fase
    if "Bottom" in fase or "Capitulação" in fase:
        insights.append("💎 Fase de máxima oportunidade - DCA agressivo recomendado")
    elif "Acumulação" in fase:
        insights.append("📈 Fase de construção de posição - boa relação risco/retorno")
    elif "Bull Médio" in fase:
        insights.append("⚖️ Mercado maduro - manter disciplina de risco")
    elif "Euforia" in fase or "Topo" in fase:
        insights.append("⚠️ Fase de realização - priorizar proteção de capital")
    
    # Insights por MVRV
    if mvrv < 1.0:
        insights.append(f"🔥 MVRV {mvrv:.1f} - território de compra histórico")
    elif mvrv > 3.0:
        insights.append(f"🚨 MVRV {mvrv:.1f} - território de venda histórico")
    
    # Insights por RSI
    if rsi_mensal < 35:
        insights.append(f"📉 RSI Mensal {rsi_mensal} - oversold extremo")
    elif rsi_mensal > 70:
        insights.append(f"📈 RSI Mensal {rsi_mensal} - overbought")
    
    return insights

@router.get("/analise-alavancagem")
async def analisar_alavancagem():
    """
    API da Camada 3: Análise de Dimensionamento
    
    Usa tabela MVRV × RSI Mensal para determinar alavancagem máxima
    """
    try:
        logging.info("⚖️ Iniciando análise de alavancagem...")
        
        # 1. Buscar dados necessários
        mvrv = obter_mvrv_do_ciclo()
        rsi_mensal = obter_rsi_mensal()  # TODO: implementar fonte real
        
        if mvrv == 0:
            return {
                "analise": "alavancagem",
                "timestamp": datetime.utcnow().isoformat(),
                "score_consolidado": 0,
                "classificacao": "erro",
                "max_leverage": 1.0,
                "acao_recomendada": "Sistema indisponível - usar apenas spot",
                "status": "error",
                "erro": "MVRV indisponível"
            }
        
        # 2. Encontrar parâmetros na tabela
        parametros = encontrar_parametros_alavancagem(mvrv, rsi_mensal)
        
        max_leverage = parametros["max_leverage"]
        fase = parametros["fase"]
        stop_loss = parametros["stop_loss"]
        
        # 3. Calcular score da oportunidade
        score_consolidado = calcular_score_alavancagem(max_leverage)
        
        # 4. Gerar análise
        classificacao = classificar_oportunidade(score_consolidado)
        acao = obter_acao_recomendada(max_leverage, fase)
        insights = get_insights_alavancagem(mvrv, rsi_mensal, fase, max_leverage)
        
        # 5. Resposta consolidada
        return {
            "analise": "alavancagem",
            "timestamp": datetime.utcnow().isoformat(),
            "score_consolidado": round(score_consolidado, 1),
            "score_maximo": 100,
            "classificacao": classificacao,
            "oportunidade_alavancagem": score_consolidado >= 60,
            "acao_recomendada": acao,
            
            "parametros": {
                "max_leverage": max_leverage,
                "stop_loss_percent": stop_loss,
                "fase_mercado": fase,
                "risk_level": "baixo" if max_leverage >= 2.5 else "médio" if max_leverage >= 2.0 else "alto"
            },
            
            "inputs": {
                "mvrv_z_score": round(mvrv, 2),
                "rsi_mensal": rsi_mensal,
                "mvrv_range": f"{parametros['mvrv_min']}-{parametros['mvrv_max']}",
                "rsi_range": f"{parametros['rsi_min']}-{parametros['rsi_max']}"
            },
            
            "analise": {
                "insights": insights,
                "confiabilidade": "alta" if rsi_mensal != obter_rsi_mensal() else "média"  # Se RSI for calculado
            },
            
            "recomendacoes": {
                "size_position": f"Usar no máximo {max_leverage}x de alavancagem",
                "stop_loss": f"Stop loss em -{stop_loss}% do patrimônio",
                "time_horizon": "Médio prazo (1-6 meses)" if max_leverage >= 2.0 else "Curto prazo (1-3 meses)"
            },
            
            "alertas": [
                f"⚠️ Não exceder {max_leverage}x de alavancagem",
                f"🛡️ Stop loss obrigatório em -{stop_loss}%",
                "📊 Reavaliar a cada mudança significativa de MVRV"
            ],
            
            "status": "success"
        }
        
    except Exception as e:
        logging.error(f"❌ Erro na análise de alavancagem: {str(e)}")
        return {
            "analise": "alavancagem",
            "timestamp": datetime.utcnow().isoformat(),
            "score_consolidado": 0,
            "classificacao": "erro",
            "max_leverage": 1.0,
            "acao_recomendada": "Sistema indisponível - usar apenas spot",
            "status": "error",
            "erro": str(e)
        }