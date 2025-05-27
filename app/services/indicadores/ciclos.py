#/app/services/indicadores/ciclo.py

from datetime import datetime

def obter_indicadores():
    # TODO: Buscar do PostgreSQL via helper
    return {
        "bloco": "ciclo",
        "timestamp": datetime.utcnow().isoformat(),
        "indicadores": {
            "MVRV_Z": {"valor": 2.1, "fonte": "Glassnode"},
            "Realized_Ratio": {"valor": 1.3, "fonte": "Glassnode"},
            "Puell_Multiple": {"valor": 1.2, "fonte": "Glassnode"}
        }
    }
