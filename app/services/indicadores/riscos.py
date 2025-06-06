# app/services/indicadores/riscos.py - ATUALIZADO

from datetime import datetime
from app.services.utils.helpers.postgres import get_dados_risco

def safe_format_number(value, divisor=1, decimals=1, suffix=""):
    """
    Formata números de forma segura, tratando valores None, Decimal e erros de conversão
    """
    if value is None:
        return f"0{'.' + '0' * decimals if decimals > 0 else ''}{suffix}"
    try:
        num = float(value) / divisor
        if decimals == 0:
            return f"{int(num)}{suffix}"
        else:
            return f"{num:.{decimals}f}{suffix}"
    except (ValueError, TypeError):
        return f"0{'.' + '0' * decimals if decimals > 0 else ''}{suffix}"

def format_currency(value):
    """Formata valor em dólares"""
    if value is None:
        return "$0.00"
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"

def obter_indicadores():
    dados_db = get_dados_risco()
    
    if dados_db:
        # Dados básicos (mantém estrutura existente)
        response = {
            "bloco": "riscos",
            "timestamp": dados_db["timestamp"].isoformat() if dados_db["timestamp"] else datetime.utcnow().isoformat(),
            "indicadores": {
                "Dist_Liquidacao": {
                    "valor": safe_format_number(dados_db['dist_liquidacao'], suffix="%"),
                    "fonte": dados_db["fonte"] or "PostgreSQL"
                },
                "Health_Factor": {
                    "valor": float(dados_db["health_factor"]) if dados_db["health_factor"] else 0.0,
                    "fonte": dados_db["fonte"] or "PostgreSQL"
                }
            },
            "status": "success",
            "fonte_dados": "PostgreSQL"
        }
        
        # NOVO: Adicionar dados da posição atual
        posicao_atual = {
            "divida_total": {
                "valor_numerico": float(dados_db["total_borrowed"]) if dados_db.get("total_borrowed") else 0.0,
                "valor_formatado": format_currency(dados_db.get("total_borrowed"))
            },
            "posicao_total": {
                "valor_numerico": float(dados_db["supplied_asset_value"]) if dados_db.get("supplied_asset_value") else 0.0,
                "valor_formatado": format_currency(dados_db.get("supplied_asset_value"))
            },
            "capital_liquido": {
                "valor_numerico": float(dados_db["net_asset_value"]) if dados_db.get("net_asset_value") else 0.0,
                "valor_formatado": format_currency(dados_db.get("net_asset_value"))
            },
            "alavancagem_atual": {
                "valor_numerico": float(dados_db["alavancagem"]) if dados_db.get("alavancagem") else 0.0,
                "valor_formatado": f"{float(dados_db['alavancagem']):.2f}x" if dados_db.get("alavancagem") else "0.00x"
            },
            "btc_price": {
                "valor_numerico": float(dados_db["btc_price"]) if dados_db.get("btc_price") else 0.0,
                "valor_formatado": format_currency(dados_db.get("btc_price"))
            }
        }
        
        response["posicao_atual"] = posicao_atual
        return response
    else:
        return {
            "bloco": "riscos",
            "timestamp": datetime.utcnow().isoformat(),
            "indicadores": {
                "Dist_Liquidacao": {"valor": None, "fonte": None},
                "Health_Factor": {"valor": None, "fonte": None}
            },
            "posicao_atual": {
                "divida_total": {"valor_numerico": 0.0, "valor_formatado": "$0.00"},
                "posicao_total": {"valor_numerico": 0.0, "valor_formatado": "$0.00"},
                "capital_liquido": {"valor_numerico": 0.0, "valor_formatado": "$0.00"},
                "alavancagem_atual": {"valor_numerico": 0.0, "valor_formatado": "0.00x"},
                "btc_price": {"valor_numerico": 0.0, "valor_formatado": "$0.00"}
            },
            "status": "no_data",
            "fonte_dados": "PostgreSQL"
        }