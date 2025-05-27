#/app/services/indicadores/momentum.py

from datetime import datetime

def obter_indicadores():
    # TODO: Buscar do PostgreSQL via helper
    return {
        "bloco": "momentum",
        "timestamp": datetime.utcnow().isoformat(),
        "indicadores": {
            "RSI_Semanal": {"valor": 52, "fonte": "TradingView"},
            "Funding_Rates": {"valor": "0.015%", "fonte": "Coinglass"},
            "OI_Change": {"valor": "+12%", "fonte": "Coinglass"},
            "Long_Short_Ratio": {"valor": 0.98, "fonte": "Binance"}
        }
    }
