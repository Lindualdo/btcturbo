# app/services/analises/analise_tatica.py - SEM FALLBACKS FIXOS

from datetime import datetime
import logging
from app.services.utils.helpers.matriz_tatica_helper import encontrar_acao_tatica, calcular_score_tatico
from app.services.utils.helpers.rsi_helper import obter_rsi_diario, obter_ema144_distance
from app.services.utils.helpers.simulacao_helper import obter_dados_posicao, simular_impacto_posicao

def calcular_analise_tatica():
    """
    Função principal: calcula análise tática completa
    FAIL FAST: Se dados críticos não disponíveis, retorna erro
    """
    try:
        logging.info("⚡ Iniciando análise tática...")
        
        # 1. Validar dados críticos - FAIL FAST
        try:
            ema_distance = obter_ema144_distance()
            logging.info(f"✅ EMA144 distance: {ema_distance:+.1f}%")
        except Exception as e:
            return {
                "analise": "tatica",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "error",
                "erro": f"EMA144 indisponível: {str(e)}",
                "componente_faltante": "ema144_distance",
                "acao_recomendada": "Corrigir fonte de dados EMAs para continuar"
            }
        
        try:
            rsi_diario = obter_rsi_diario()
            logging.info(f"✅ RSI Diário: {rsi_diario:.1f}")
        except Exception as e:
            return {
                "analise": "tatica",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "error",
                "erro": f"RSI Diário indisponível: {str(e)}",
                "componente_faltante": "rsi_diario",
                "acao_recomendada": "Corrigir conexão TradingView para continuar"
            }
        
        # 2. Buscar dados de posição (opcional)
        posicao_atual = None
        try:
            posicao_atual = obter_dados_posicao()
            if posicao_atual:
                logging.info("✅ Dados de posição obtidos")
            else:
                logging.warning("⚠️ Dados de posição não disponíveis")
        except Exception as e:
            logging.warning(f"⚠️ Erro obtendo posição: {str(e)}")
        
        # 3. Encontrar ação na matriz - dados críticos OK
        regra_tatica = encontrar_acao_tatica(ema_distance, rsi_diario)
        
        acao = regra_tatica["acao"]
        tamanho = regra_tatica["tamanho"]
        justificativa = regra_tatica["justificativa"]
        
        # 4. Calcular score da oportunidade
        score_consolidado = calcular_score_tatico(acao, tamanho, ema_distance, rsi_diario)
        
        # 5. Classificações e insights
        classificacao = _classificar_oportunidade(score_consolidado)
        acao_recomendada = _formatar_acao_recomendada(acao, tamanho, justificativa)
        insights = _gerar_insights(acao, tamanho, ema_distance, rsi_diario)
        
        # 6. Simular impacto (se dados disponíveis)
        simulacao = None
        if posicao_atual:
            try:
                simulacao = simular_impacto_posicao(acao, tamanho, posicao_atual)
                if "erro" in simulacao:
                    logging.warning(f"⚠️ Erro na simulação: {simulacao['erro']}")
                    simulacao = None
            except Exception as e:
                logging.warning(f"⚠️ Erro na simulação: {str(e)}")
        
        # 7. Alertas
        alertas = _gerar_alertas(acao, tamanho, ema_distance, rsi_diario, score_consolidado, simulacao)
        
        # 8. Resposta consolidada
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
                "momentum": "forte" if abs(rsi_diario - 50) > 20 else "fraco",
                "dados_posicao_disponiveis": posicao_atual is not None
            },
            
            "alertas": alertas,
            "status": "success"
        }
        
        # Adicionar simulação se disponível
        if simulacao:
            response["simulacao"] = simulacao
        else:
            response["simulacao"] = {
                "status": "indisponivel",
                "motivo": "Dados de posição não encontrados ou inválidos"
            }
        
        logging.info(f"✅ Análise tática concluída: {acao} {tamanho}% (score: {score_consolidado:.1f})")
        return response
        
    except Exception as e:
        logging.error(f"❌ Erro inesperado na análise tática: {str(e)}")
        return {
            "analise": "tatica",
            "timestamp": datetime.utcnow().isoformat(),
            "score_consolidado": 0,
            "classificacao": "erro",
            "acao_recomendada": "Sistema com falha crítica - não operar",
            "status": "error",
            "erro": f"Erro inesperado: {str(e)}",
            "componente_faltante": "sistema"
        }

# Funções auxiliares privadas - SEM ALTERAÇÕES
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
    
    # Insights contextuais
    if abs(ema_distance) > 15:
        insights.append(f"📊 Preço {'muito acima' if ema_distance > 0 else 'muito abaixo'} da EMA144")
    
    if rsi_diario < 30:
        insights.append("📉 RSI em território oversold")
    elif rsi_diario > 70:
        insights.append("📈 RSI em território overbought")
    
    return insights

def _gerar_alertas(acao: str, tamanho: int, ema_distance: float, rsi_diario: float, score: float, simulacao: dict) -> list:
    """Gera alertas táticos"""
    alertas = [
        f"📊 EMA144: {ema_distance:+.1f}% | RSI: {rsi_diario:.0f}",
        f"🎯 Ação sugerida: {acao} {tamanho}%" if tamanho > 0 else "🎯 Manter posição atual"
    ]
    
    # Alerta de timing
    if score >= 80:
        alertas.append("🚨 Oportunidade excelente - executar imediatamente")
    elif score >= 70:
        alertas.append("⏰ Boa oportunidade - executar dentro de 24h")
    elif score >= 50:
        alertas.append("⏰ Oportunidade neutra - monitorar evolução")
    else:
        alertas.append("⚠️ Condições desfavoráveis - aguardar")
    
    # Alertas de simulação
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
    if score >= 80:
        return "imediato"
    elif score >= 70:
        return "24_horas"
    elif score >= 50:
        return "monitorar"
    else:
        return "aguardar"