# app/services/utils/helpers/dashboard_home/estrategia_response_helper.py

import logging

logger = logging.getLogger(__name__)

def criar_resposta_estrategia(acao: str, tamanho_percent: int, cenario: str, 
                             justificativa: str, urgencia: str, matriz_usada: str,
                             dados_tecnicos: dict, fonte: str = None) -> dict:
    """
    Cria resposta padronizada para estratégia (proteções + matrizes)
    
    Args:
        acao: Ação específica (ex: "ADICIONAR", "Reduzir alavancagem em $1,500.00")
        tamanho_percent: Percentual da operação
        cenario: Cenário/fase identificada
        justificativa: Justificativa específica
        urgencia: Nível de urgência
        matriz_usada: Tipo de matriz/validação usada
        dados_tecnicos: Dados técnicos para estrutura completa
        fonte: Fonte da decisão (opcional)
    
    Returns:
        dict: Resposta formatada para PostgreSQL + JSON frontend
    """
    logger.info(f"📋 Criando resposta: {acao} ({tamanho_percent}%) - {matriz_usada}")
    
    # Campos para PostgreSQL (compatibilidade total)
    campos_estrategia = {
        "acao_estrategia": acao,
        "tamanho_percent_estrategia": tamanho_percent,
        "cenario_estrategia": cenario,
        "justificativa_estrategia": justificativa,
        "urgencia_estrategia": urgencia,
        "ema_distance": dados_tecnicos.get("ema_distance", 0.0),
        "ema_valor": dados_tecnicos.get("ema_valor", 0.0),
        "rsi_diario": dados_tecnicos.get("rsi_diario", 0.0),
        "matriz_usada": matriz_usada
    }
    
    # JSON para frontend (compatibilidade total)
    json_estrategia = {
        "acao": acao,
        "tamanho_percent": tamanho_percent,
        "cenario": cenario,
        "justificativa": justificativa,
        "urgencia": urgencia,
        "dados_decisao": {
            "btc_price": dados_tecnicos.get("btc_price", 0.0),
            "ema_valor": dados_tecnicos.get("ema_valor", 0.0),
            "ema_distance": dados_tecnicos.get("ema_distance", 0.0),
            "rsi_diario": dados_tecnicos.get("rsi_diario", 0.0),
            "score_mercado": dados_tecnicos.get("score_mercado", 0.0),
            "score_risco": dados_tecnicos.get("score_risco", 0.0),
            "mvrv": dados_tecnicos.get("mvrv_valor", 0.0),
            "matriz_usada": matriz_usada,
            "data_timestamp": dados_tecnicos.get("data_timestamp", ""),
            "calculated_distance": dados_tecnicos.get("calculated_distance", dados_tecnicos.get("ema_distance", 0.0))
        }
    }
    
    return {
        "status": "success",
        "campos": campos_estrategia,
        "json": json_estrategia,
        "modulo": "estrategia",
        "fonte": fonte or matriz_usada
    }