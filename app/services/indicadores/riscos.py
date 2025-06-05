# app/services/indicadores/riscos.py

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

def obter_indicadores():
    dados_db = get_dados_risco()
    
    if dados_db:
        return {
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
    else:
        return {
            "bloco": "riscos",
            "timestamp": datetime.utcnow().isoformat(),
            "indicadores": {
                "Dist_Liquidacao": {"valor": None, "fonte": None},
                "Health_Factor": {"valor": None, "fonte": None}
            },
            "status": "no_data",
            "fonte_dados": "PostgreSQL"
        }