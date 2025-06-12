# app/services/utils/helpers/dashboard_home/filtros_protecao_helper.py

import logging
from .fase_mercado_helper import identificar_fase_mercado
from .estrategia_response_helper import criar_resposta_estrategia

logger = logging.getLogger(__name__)

def aplicar_filtros_protecao(dados_dashboard: dict, mvrv_valor: float, ema_distance: float, 
                            rsi_diario: float, btc_price: float, ema_valor: float, 
                            data_timestamp: str) -> dict:
    """
    Aplica filtros de proteção: mercado, risco e alavancagem
    
    Returns:
        dict: Ação de proteção ou None se passou nos filtros
    """
    # Extrair dados necessários
    mercado_data = dados_dashboard.get("mercado", {})
    risco_data = dados_dashboard.get("risco", {})
    alavancagem_data = dados_dashboard.get("alavancagem", {})
    
    score_mercado = float(mercado_data.get("campos", {}).get("score_mercado", 0))
    score_risco = float(risco_data.get("campos", {}).get("score_risco", 0))
    
    # Dados de alavancagem
    alavancagem_atual = float(alavancagem_data.get("campos", {}).get("alavancagem_atual", 0))
    max_permitida = float(alavancagem_data.get("campos", {}).get("alavancagem_permitida", 3.0))
    valor_a_reduzir = float(alavancagem_data.get("campos", {}).get("valor_a_reduzir", 0))
    valor_a_reduzir_formatado = alavancagem_data.get("json", {}).get("valor_a_reduzir_formatado", "$0.00")
    posicao_total = float(alavancagem_data.get("campos", {}).get("posicao_total", 0))
    
    # Identificar fase do mercado
    fase_mercado = identificar_fase_mercado(mvrv_valor)
    
    # Dados de contexto
    dados_contexto = _extrair_dados_contexto(
        score_mercado, score_risco, ema_distance, ema_valor, 
        rsi_diario, btc_price, data_timestamp, mvrv_valor
    )
    
    logger.info("🛡️ Verificando filtros de proteção...")
    logger.info(f"📊 Score Mercado: {score_mercado:.1f}, Score Risco: {score_risco:.1f}")
    logger.info(f"⚡ Alavancagem: {alavancagem_atual:.2f}x (max: {max_permitida:.2f}x)")
    
    # Filtro 1: Mercado desfavorável
    if score_mercado < 40:
        logger.warning(f"🚨 FILTRO ACIONADO: Mercado desfavorável ({score_mercado:.1f} < 40)")
        return criar_resposta_estrategia(
            acao=f"Reduzir exposição - mercado {fase_mercado}",
            tamanho_percent=50,
            cenario=fase_mercado,
            justificativa=f"Score mercado {score_mercado:.1f} abaixo do limite 40.0",
            urgencia="critica",
            matriz_usada="Validação ciclo",
            dados_tecnicos=dados_contexto,
            fonte="filtros_protecao"
        )
    
    # Filtro 2: Risco crítico
    if score_risco < 50:
        logger.warning(f"🚨 FILTRO ACIONADO: Risco crítico ({score_risco:.1f} < 50)")
        return criar_resposta_estrategia(
            acao=f"Reduzir risco - mercado {fase_mercado}",
            tamanho_percent=70,
            cenario=fase_mercado,
            justificativa=f"Score risco {score_risco:.1f} abaixo do limite 50.0",
            urgencia="critica",
            matriz_usada="Validação Risco",
            dados_tecnicos=dados_contexto,
            fonte="filtros_protecao"
        )
    
    # Filtro 3: Overleveraged
    if alavancagem_atual > max_permitida:
        # Calcular tamanho percentual correto
        tamanho_percent = (valor_a_reduzir / posicao_total * 100) if posicao_total > 0 else 0
        
        logger.warning(f"🚨 FILTRO ACIONADO: Overleveraged ({alavancagem_atual:.2f}x > {max_permitida:.2f}x)")
        logger.warning(f"📉 Valor a reduzir: {valor_a_reduzir_formatado} ({tamanho_percent:.1f}%)")
        return criar_resposta_estrategia(
            acao=f"Reduzir alavancagem em {valor_a_reduzir_formatado}",
            tamanho_percent=int(tamanho_percent),
            cenario=fase_mercado,
            justificativa=f"Alavancagem {alavancagem_atual:.2f}x excede permitido {max_permitida:.2f}x em {alavancagem_atual-max_permitida:.2f}x",
            urgencia="critica",
            matriz_usada="Validação Alavancagem",
            dados_tecnicos=dados_contexto,
            fonte="filtros_protecao"
        )
    
    logger.info("✅ Todos os filtros de proteção passaram - prosseguindo para matrizes")
    return None  # Passou nos filtros

def _extrair_dados_contexto(score_mercado: float, score_risco: float, ema_distance: float, 
                           ema_valor: float, rsi_diario: float, btc_price: float, 
                           data_timestamp: str, mvrv_valor: float) -> dict:
    """Extrai dados de contexto para estrutura completa"""
    return {
        "score_mercado": score_mercado,
        "score_risco": score_risco,
        "ema_distance": ema_distance,
        "ema_valor": ema_valor,
        "rsi_diario": rsi_diario,
        "btc_price": btc_price,
        "data_timestamp": data_timestamp,
        "mvrv_valor": mvrv_valor
    }