# app/services/analise_tatica.py

from datetime import datetime
import logging
from app.services.utils.helpers.matriz_tatica_helper import encontrar_acao_tatica, calcular_score_tatico
from app.services.utils.helpers.rsi_helper import obter_rsi_diario, obter_ema144_distance
from app.services.utils.helpers.simulacao_helper import obter_dados_posicao, simular_impacto_posicao

def calcular_analise_tatica():
    """
    Função principal: calcula análise tática completa
    """
    try:
        logging.info("⚡ Iniciando análise tática...")
        
        # 1. Buscar dados necessários
        ema_distance = obter_ema144_distance()
        rsi_diario = obter_rsi_diario()
        posicao_atual = obter_dados_posicao()
        
        # 2. Encontrar ação na matriz
        regra_tatica = encontrar_acao_tatica(ema_distance, rsi_diario)
        
        acao = regra_tatica["acao"]
        tamanho = regra_tatica["tamanho"]
        justificativa = regra_tatica["justificativa"]
        
        # 3. Calcular score da oportunidade
        score_consolidado = calcular_score_tatico(acao, tamanho, ema_distance, rsi_diario)
        
        # 4. Classificações e insights
        classificacao = _classificar_oportunidade(score_consolidado)
        acao_recomendada = _formatar_acao_recomendada(acao, tamanho, justificativa)
        insights = _gerar_insights(acao, tamanho, ema_distance, rsi_diario)
        
        # 5. Simular impacto
        simulacao = simular_impacto_posicao(acao, tamanho, posicao_atual) if posicao_atual else None
        
        # 6. Alertas
        alertas = _gerar_alertas(acao, tamanho, ema_distance, rsi_diario, score_consolidado, simulacao)
        
        # 7. Resposta consolidada
        response = {
            "analise": "tatica",
            "timestamp": datetime.utcnow().isoformat(),
            "score_consolidado": round(score_consolidado, 1),
            "score_maximo": 100,
            "classificacao": classificacao,
            "acao_recomendada": acao_recomendada,
            
            "decisao_tatica": {
                "acao": acao,
                "tamanho_percent": tamanho,
                "justificativa": justificativa,
                "confianca": _avaliar_confianca(score_consolidado)
            },
            
            "inputs": {
                "ema144_distance_percent": round(ema_distance, 1),
                "rsi_diario": round(rsi_diario, 0),
                "ema_range": f"{regra_tatica['ema_min']} a {regra_tatica['ema_max']}%",
                "rsi_range": f"{regra_tatica['rsi_min']}-{regra_tatica['rsi_max']}"
            },
            
            "analise": {
                "insights": insights,
                "timing": _avaliar_timing(score_consolidado),
                "contexto_mercado": "bullish" if ema_distance > 0 else "bearish",
                "momentum": "forte" if abs(rsi_diario - 50) > 20 else "fraco"
            },
            
            "alertas": alertas,
            "status": "success"
        }
        
        if simulacao and "erro" not in simulacao:
            response["simulacao"] = simulacao
        
        return response
        
    except Exception as e:
        logging.error(f"❌ Erro na análise tática: {str(e)}")
        return {
            "analise": "tatica",
            "timestamp": datetime.utcnow().isoformat(),
            "score_consolidado": 0,
            "classificacao": "erro",
            "acao_recomendada": "Sistema indisponível - não operar",
            "status": "error",
            "erro": str(e)
        }

# Funções auxiliares privadas
def _classificar_oportunidade(score: float) -> str:
    """Classifica oportunidade tática"""
    if score >= 80:
        return "excelente"
    elif score >= 65:
        return "boa"
    elif score >= 50:
        return "neutra"
    else:
        return "ruim"

def _formatar_acao_recomendada(acao: str, tamanho: int, justificativa: str) -> str:
    """Formata ação recomendada"""
    if tamanho > 0:
        return f"{acao} {tamanho}% da posição - {justificativa.lower()}"
    else:
        return f"Manter posição atual - {justificativa.lower()}"

def _gerar_insights(acao: str, tamanho: int, ema_distance: float, rsi_diario: float) -> list:
    """Gera insights táticos"""
    insights = []
    
    if acao == "ADICIONAR":
        insights.append("💎 Oportunidade de acumulação identificada")
        if tamanho >= 50:
            insights.append("🔥 Oportunidade de alta convicção")
    elif acao == "REALIZAR":
        insights.append("💰 Momento de proteção de lucros")
        if tamanho >= 30:
            insights.append("⚠️ Sinal forte de topo local")
    else:
        insights.append("⏳ Aguardar melhores condições de entrada/saída")
    
    return insights

def _gerar_alertas(acao: str, tamanho: int, ema_distance: float, rsi_diario: float, score: float, simulacao: dict) -> list:
    """Gera alertas táticos"""
    alertas = [
        f"📊 EMA144: {ema_distance:+.1f}% | RSI: {rsi_diario:.0f}",
        f"🎯 Ação sugerida: {acao} {tamanho}%" if tamanho > 0 else "🎯 Manter posição atual",
        "⏰ Executar dentro de 24h" if score >= 70 else "⏰ Monitorar evolução"
    ]
    
    if simulacao and "erro" not in simulacao:
        if acao == "ADICIONAR":
            alertas.append(f"💰 Impacto: {simulacao['impacto']} = {simulacao['valor_operacao']}")
        elif acao == "REALIZAR":
            alertas.append(f"💸 Realização: {simulacao['impacto']} = {simulacao['valor_operacao']}")
    
    return alertas

def _avaliar_confianca(score: float) -> str:
    """Avalia confiança da decisão"""
    if score >= 70:
        return "alta"
    elif score >= 50:
        return "média"
    else:
        return "baixa"

def _avaliar_timing(score: float) -> str:
    """Avalia timing da execução"""
    if score >= 70:
        return "imediato"
    else:
        return "aguardar melhores condições"