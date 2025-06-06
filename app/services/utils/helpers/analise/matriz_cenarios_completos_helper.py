# app/services/utils/helpers/matriz_cenarios_completos_helper.py

import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

# 8 CENÁRIOS DA ESPECIFICAÇÃO v5.0 - MATRIZ COMPLETA
CENARIOS_COMPLETOS = [
    {
        "id": "bull_inicial",
        "nome": "Bull Market Inicial",
        "descricao": "Bitcoin saindo de acumulação",
        "condicoes": {
            "score_mercado_min": 70,
            "score_risco_min": 80,
            "mvrv_min": 1.0,
            "mvrv_max": 2.0,
            "ema_distance_min": -5,
            "ema_distance_max": 10,
            "rsi_diario_min": 35,
            "rsi_diario_max": 55
        },
        "acao": {
            "decisao": "ENTRAR",
            "alavancagem_recomendada": 2.0,
            "stop_loss": 12,
            "target": "Aguardar EMA +15%",
            "justificativa": "Estrutura bullish se formando com risco controlado"
        },
        "prioridade": 1,
        "score_bonus": 20
    },
    
    {
        "id": "bull_maduro",
        "nome": "Bull Market Maduro",
        "descricao": "Tendência estabelecida há meses",
        "condicoes": {
            "score_mercado_min": 65,
            "score_risco_min": 70,
            "mvrv_min": 2.0,
            "mvrv_max": 3.0,
            "ema_distance_min": 10,
            "ema_distance_max": 20,
            "rsi_diario_min": 60,
            "rsi_diario_max": 75
        },
        "acao": {
            "decisao": "REALIZAR_PARCIAL",
            "tamanho_percent": 25,
            "alavancagem_recomendada": 1.5,
            "stop_loss": 10,
            "target": "Preparar mais realizações",
            "justificativa": "Mercado maduro - proteção de lucros"
        },
        "prioridade": 2,
        "score_bonus": 15
    },
    
    {
        "id": "topo_formando",
        "nome": "Topo Formando",
        "descricao": "Euforia de mercado - sinais de topo",
        "condicoes": {
            "score_mercado_min": 60,
            "score_risco_min": 65,
            "mvrv_min": 3.0,
            "mvrv_max": 999,
            "ema_distance_min": 20,
            "ema_distance_max": 999,
            "rsi_diario_min": 75,
            "rsi_diario_max": 100
        },
        "acao": {
            "decisao": "REALIZAR_AGRESSIVO",
            "tamanho_percent": 50,
            "alavancagem_recomendada": 1.0,
            "stop_loss": 8,
            "target": "Reduzir para 1.0-1.5x max",
            "justificativa": "Sinais de topo - proteção urgente"
        },
        "prioridade": 1,
        "score_bonus": 25
    },
    
    {
        "id": "correcao_bull",
        "nome": "Correção em Bull",
        "descricao": "Pullback saudável em tendência bullish",
        "condicoes": {
            "score_mercado_min": 60,
            "score_risco_min": 75,
            "mvrv_min": 1.5,
            "mvrv_max": 3.0,
            "ema_distance_min": -15,
            "ema_distance_max": -5,
            "rsi_diario_min": 30,
            "rsi_diario_max": 50
        },
        "acao": {
            "decisao": "ADICIONAR_AGRESSIVO",
            "tamanho_percent": 40,
            "alavancagem_recomendada": 2.0,
            "stop_loss": 10,
            "target": "DCA em 3 dias",
            "justificativa": "Correção saudável - oportunidade"
        },
        "prioridade": 1,
        "score_bonus": 22
    },
    
    {
        "id": "inicio_bear",
        "nome": "Início Bear Market",
        "descricao": "Quebra de estrutura bullish",
        "condicoes": {
            "score_mercado_min": 0,
            "score_mercado_max": 45,
            "score_risco_min": 60,
            "mvrv_min": 1.5,
            "mvrv_max": 3.0,
            "ema_distance_min": -15,
            "ema_distance_max": 5,
            "rsi_diario_min": 25,
            "rsi_diario_max": 45
        },
        "acao": {
            "decisao": "REDUZIR_DEFENSIVO",
            "tamanho_percent": 50,
            "alavancagem_recomendada": 0.5,
            "stop_loss": 15,
            "target": "Preservação capital",
            "justificativa": "Estrutura quebrada - modo defensivo"
        },
        "prioridade": 2,
        "score_bonus": -10
    },
    
    {
        "id": "bear_profundo",
        "nome": "Bear Market Profundo",
        "descricao": "Capitulação geral - oportunidade histórica",
        "condicoes": {
            "score_mercado_min": 0,
            "score_mercado_max": 30,
            "score_risco_min": 40,
            "mvrv_min": 0.0,
            "mvrv_max": 1.5,
            "ema_distance_min": -999,
            "ema_distance_max": -15,
            "rsi_diario_min": 15,
            "rsi_diario_max": 35
        },
        "acao": {
            "decisao": "ACUMULAR_HISTORICO",
            "tamanho_percent": 75,
            "alavancagem_recomendada": 1.5,
            "stop_loss": 20,
            "target": "Aguardar Score > 60",
            "justificativa": "Oportunidade histórica de acumulação"
        },
        "prioridade": 1,
        "score_bonus": 30
    },
    
    {
        "id": "risco_critico",
        "nome": "Risco Crítico",
        "descricao": "Posição em perigo - override obrigatório",
        "condicoes": {
            "score_risco_max": 40,
            "health_factor_max": 1.3,
            "dist_liquidacao_max": 25
        },
        "acao": {
            "decisao": "EMERGENCIA_REDUZIR",
            "tamanho_percent": 80,
            "alavancagem_recomendada": 0.2,
            "stop_loss": 5,
            "target": "Salvar capital",
            "justificativa": "EMERGÊNCIA: Posição em risco crítico"
        },
        "prioridade": 0,  # Máxima prioridade
        "score_bonus": -50,
        "override": True
    },
    
    {
        "id": "volatilidade_comprimida",
        "nome": "Volatilidade Comprimida",
        "descricao": "Mercado lateral - breakout iminente",
        "condicoes": {
            "score_mercado_min": 50,
            "score_mercado_max": 65,
            "score_risco_min": 70,
            "bbw_max": 8,
            "rsi_diario_min": 45,
            "rsi_diario_max": 55,
            "ema_distance_min": -5,
            "ema_distance_max": 5
        },
        "acao": {
            "decisao": "PREPARAR_BREAKOUT",
            "tamanho_percent": 0,
            "alavancagem_recomendada": 1.2,
            "stop_loss": 8,
            "target": "50% dry powder",
            "justificativa": "Compressão - preparar para movimento"
        },
        "prioridade": 3,
        "score_bonus": 5
    }
]

def avaliar_cenario_completo(
    score_mercado: float,
    score_risco: float,
    mvrv: float,
    ema_distance: float,
    rsi_diario: float,
    dados_extras: Dict = None
) -> Tuple[Dict, str]:
    """
    Avalia qual cenário completo se aplica baseado em todas as condições
    
    Returns:
        Tuple[cenario_encontrado, motivo_escolha]
    """
    
    dados_extras = dados_extras or {}
    health_factor = dados_extras.get("health_factor", 999)
    dist_liquidacao = dados_extras.get("dist_liquidacao", 100)
    bbw = dados_extras.get("bbw_percentage", 15)
    
    logger.info(f"🔍 Avaliando cenários: Mercado={score_mercado}, Risco={score_risco}, MVRV={mvrv}, EMA={ema_distance:+.1f}%, RSI={rsi_diario}")
    
    # Ordenar por prioridade (0 = maior prioridade)
    cenarios_ordenados = sorted(CENARIOS_COMPLETOS, key=lambda x: x["prioridade"])
    
    for cenario in cenarios_ordenados:
        if _verificar_condicoes_cenario(cenario, score_mercado, score_risco, mvrv, 
                                       ema_distance, rsi_diario, health_factor, 
                                       dist_liquidacao, bbw):
            
            motivo = f"Cenário '{cenario['nome']}' atendeu todas as condições (prioridade {cenario['prioridade']})"
            logger.info(f"✅ {motivo}")
            
            return cenario, motivo
    
    # Fallback: usar matriz tática básica (EMA+RSI)
    motivo = "Nenhum cenário específico atendido - usando matriz tática básica como fallback"
    logger.warning(f"⚠️ {motivo}")
    
    return None, motivo

def _verificar_condicoes_cenario(
    cenario: Dict,
    score_mercado: float,
    score_risco: float,
    mvrv: float,
    ema_distance: float,
    rsi_diario: float,
    health_factor: float,
    dist_liquidacao: float,
    bbw: float
) -> bool:
    """Verifica se todas as condições do cenário são atendidas"""
    
    condicoes = cenario["condicoes"]
    
    try:
        # Score Mercado
        if "score_mercado_min" in condicoes:
            if score_mercado < condicoes["score_mercado_min"]:
                return False
        if "score_mercado_max" in condicoes:
            if score_mercado > condicoes["score_mercado_max"]:
                return False
        
        # Score Risco
        if "score_risco_min" in condicoes:
            if score_risco < condicoes["score_risco_min"]:
                return False
        if "score_risco_max" in condicoes:
            if score_risco > condicoes["score_risco_max"]:
                return False
        
        # MVRV
        if "mvrv_min" in condicoes:
            if mvrv < condicoes["mvrv_min"]:
                return False
        if "mvrv_max" in condicoes:
            if mvrv >= condicoes["mvrv_max"]:
                return False
        
        # EMA Distance
        if "ema_distance_min" in condicoes:
            if ema_distance < condicoes["ema_distance_min"]:
                return False
        if "ema_distance_max" in condicoes:
            if ema_distance > condicoes["ema_distance_max"]:
                return False
        
        # RSI Diário
        if "rsi_diario_min" in condicoes:
            if rsi_diario < condicoes["rsi_diario_min"]:
                return False
        if "rsi_diario_max" in condicoes:
            if rsi_diario > condicoes["rsi_diario_max"]:
                return False
        
        # Health Factor (específico para risco crítico)
        if "health_factor_max" in condicoes:
            if health_factor > condicoes["health_factor_max"]:
                return False
        
        # Distância Liquidação (específico para risco crítico)
        if "dist_liquidacao_max" in condicoes:
            if dist_liquidacao > condicoes["dist_liquidacao_max"]:
                return False
        
        # BBW (específico para volatilidade comprimida)
        if "bbw_max" in condicoes:
            if bbw > condicoes["bbw_max"]:
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro verificando condições do cenário {cenario['id']}: {str(e)}")
        return False

def calcular_score_cenario_completo(
    cenario: Dict,
    score_base_tatico: float,
    score_mercado: float,
    score_risco: float
) -> float:
    """
    Calcula score final considerando:
    1. Score base da matriz tática (EMA+RSI)
    2. Bonus/penalidade do cenário
    3. Pesos das outras camadas
    """
    
    score_bonus = cenario.get("score_bonus", 0)
    
    # Score base = 40% tático + 30% mercado + 30% risco
    score_integrado = (
        (score_base_tatico * 0.4) +
        (score_mercado * 0.3) +
        (score_risco * 0.3)
    )
    
    # Aplicar bonus do cenário
    score_final = score_integrado + score_bonus
    
    # Garantir range 0-100
    score_final = max(0, min(100, score_final))
    
    logger.info(f"📊 Score final: {score_final:.1f} = {score_integrado:.1f} + {score_bonus} (bonus)")
    
    return score_final

def gerar_insights_cenario(cenario: Dict, dados_contexto: Dict) -> List[str]:
    """Gera insights específicos do cenário identificado"""
    
    insights = []
    cenario_id = cenario["id"]
    acao_decisao = cenario["acao"]["decisao"]
    
    # Insight principal do cenário
    insights.append(f"🎯 Cenário identificado: {cenario['nome']}")
    
    # Insights específicos por cenário
    if cenario_id == "bull_inicial":
        insights.append("🚀 Momento ideal para construir posição")
        insights.append("💡 Risco controlado permite alavancagem moderada")
        
    elif cenario_id == "bull_maduro":
        insights.append("⚖️ Mercado maduro - balancear ganhos vs risco")
        insights.append("💰 Considerar realizações parciais")
        
    elif cenario_id == "topo_formando":
        insights.append("🚨 Sinais de topo - priorizar proteção")
        insights.append("📉 Euforia excessiva detectada")
        
    elif cenario_id == "correcao_bull":
        insights.append("💎 Oportunidade de acumulação em correção")
        insights.append("📈 Estrutura bullish permanece intacta")
        
    elif cenario_id == "inicio_bear":
        insights.append("⚠️ Estrutura bullish comprometida")
        insights.append("🛡️ Priorizar preservação de capital")
        
    elif cenario_id == "bear_profundo":
        insights.append("🔥 Oportunidade histórica de acumulação")
        insights.append("💎 Capitulação oferece preços excepcionais")
        
    elif cenario_id == "risco_critico":
        insights.append("🚨 EMERGÊNCIA: Posição em risco extremo")
        insights.append("⛑️ Ação imediata obrigatória")
        
    elif cenario_id == "volatilidade_comprimida":
        insights.append("🎪 Preparar para breakout iminente")
        insights.append("⏳ Paciência até direção definir")
    
    # Insights de contexto
    mvrv = dados_contexto.get("mvrv", 0)
    if mvrv < 1:
        insights.append(f"🔥 MVRV {mvrv:.1f} - território historicamente barato")
    elif mvrv > 3:
        insights.append(f"🚨 MVRV {mvrv:.1f} - território historicamente caro")
    
    return insights

def gerar_alertas_cenario(cenario: Dict, dados_contexto: Dict) -> List[str]:
    """Gera alertas específicos do cenário"""
    
    alertas = []
    acao = cenario["acao"]
    
    # Alerta principal
    if acao["decisao"] == "EMERGENCIA_REDUZIR":
        alertas.append("🚨 EMERGÊNCIA: Reduzir posição IMEDIATAMENTE")
    elif "REALIZAR" in acao["decisao"]:
        alertas.append(f"💰 Realizar {acao.get('tamanho_percent', 25)}% da posição")
    elif "ADICIONAR" in acao["decisao"]:
        alertas.append(f"💎 Adicionar {acao.get('tamanho_percent', 35)}% à posição")
    elif acao["decisao"] == "ENTRAR":
        alertas.append(f"🚀 Entrar com {acao['alavancagem_recomendada']}x de alavancagem")
    
    # Alertas de risco
    stop_loss = acao.get("stop_loss", 10)
    alertas.append(f"🛡️ Stop loss: -{stop_loss}% do patrimônio")
    
    # Alertas de timing
    if cenario.get("override"):
        alertas.append("⚡ PRIORIDADE MÁXIMA - Executar sem delay")
    elif cenario["prioridade"] <= 1:
        alertas.append("⏰ Alta prioridade - Executar em 24h")
    else:
        alertas.append("📅 Monitorar evolução")
    
    return alertas