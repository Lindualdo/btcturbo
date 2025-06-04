# app/utils/dashboard_helpers.py

def format_score_for_display(score: float) -> int:
    """Converte score 0-10 para 0-100 para display"""
    return round(score * 10)

def get_classification_from_score(score: float) -> str:
    """Classificação padronizada"""
    if score >= 8.0: return "ótimo"
    elif score >= 6.0: return "bom"
    elif score >= 4.0: return "neutro"
    elif score >= 2.0: return "ruim"
    else: return "crítico"

def calculate_kelly_criterion(score: float) -> str:
    """Kelly Criterion simplificado"""
    if score >= 8.0: return "75%"
    elif score >= 6.0: return "50%" 
    elif score >= 4.0: return "25%"
    elif score >= 2.0: return "10%"
    else: return "0%"

def determine_action(score: float) -> str:
    """Ação recomendada simplificada"""
    if score >= 8.0: return "Aumentar posição"
    elif score >= 6.0: return "Manter posição"
    elif score >= 4.0: return "Posição neutra"
    elif score >= 2.0: return "Reduzir exposição"
    else: return "Zerar alavancagem"

def format_response_for_dashboard(dados_api: dict) -> dict:
    """Padroniza resposta da API para dashboard"""
    return {
        "score_geral": format_score_for_display(dados_api.get("score_final", 0)),
        "classificacao": dados_api.get("classificacao", "erro"),
        "kelly": dados_api.get("kelly", "0%"),
        "acao": dados_api.get("acao", "Sistema indisponível"),
        "blocos": {
            nome: {
                "score": format_score_for_display(bloco.get("score_consolidado", 0)),
                "classificacao": bloco.get("classificacao_consolidada", "erro")
            }
            for nome, bloco in dados_api.get("blocos", {}).items()
        },
        "alertas": dados_api.get("alertas", []),
        "timestamp": dados_api.get("timestamp", "")
    }

def validate_gauge_config(gauge: dict) -> bool:
    """Valida configuração de gauge"""
    required_fields = ["id", "title"]
    return all(field in gauge for field in required_fields)

def get_gauge_by_id(gauge_id: str, gauges_list: list) -> dict:
    """Busca gauge por ID"""
    for gauge in gauges_list:
        if gauge.get("id") == gauge_id:
            return gauge
    return {}

def build_dashboard_context(request, config: dict) -> dict:
    """Constrói context completo para template"""
    return {
        "request": request,
        "current_page": "home",
        "versao": config["versao"],
        "subtitle": config["subtitle"],
        "config": {
            "versao": config["versao"],
            "api_endpoint": config["api_endpoint"],
            "novos_pesos": config["pesos_blocos"]
        },
        "gauges": config["gauges"]
    }