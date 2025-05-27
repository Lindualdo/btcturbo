#/app/services/indicadores/risscos.py

from datetime import datetime

def obter_indicadores():
    # TODO: Buscar do PostgreSQL via helper
    return {
        "bloco": "riscos",
        "timestamp": datetime.utcnow().isoformat(),
        "indicadores": {
            "Dist_Liquidacao": {"valor": "35%", "fonte": "AAVE"},
            "Health_Factor": {"valor": 1.7, "fonte": "AAVE"},
            "Exchange_Netflow": {"valor": "-5k", "fonte": "Glassnode"},
            "Stablecoin_Ratio": {"valor": "8%", "fonte": "Glassnode"}
        }
    }
