# app/services/indicadores/momentum.py

from datetime import datetime
from app.services.utils.helpers.postgres import get_dados_momentum

def obter_indicadores():
    dados_db = get_dados_momentum()
    
    if dados_db:
        return {
            "bloco": "momentum",
            "timestamp": dados_db["timestamp"].isoformat() if dados_db["timestamp"] else datetime.utcnow().isoformat(),
            "indicadores": {
                "RSI_Semanal": {
                    "valor": float(dados_db["rsi_semanal"]) if dados_db["rsi_semanal"] else 0.0,
                    "fonte": dados_db["fonte"] or "PostgreSQL"
                },
                "Funding_Rates": {
                    "valor": f"{float(dados_db['funding_rates']) * 100:.3f}%" if dados_db["funding_rates"] else "0.000%",
                    "fonte": dados_db["fonte"] or "PostgreSQL"
                },
                "Exchange_Netflow": {
                    "valor": float(dados_db["exchange_netflow"]) if dados_db["exchange_netflow"] else 0.0,
                    "fonte": dados_db["fonte"] or "PostgreSQL"
                },
                "Long_Short_Ratio": {
                    "valor": float(dados_db["long_short_ratio"]) if dados_db["long_short_ratio"] else 0.0,
                    "fonte": dados_db["fonte"] or "PostgreSQL"
                }
            },
            "status": "success",
            "fonte_dados": "PostgreSQL"
        }
    else:
        return {
            "bloco": "momentum",
            "timestamp": datetime.utcnow().isoformat(),
            "indicadores": {
                "RSI_Semanal": {"valor": None, "fonte": None},
                "Funding_Rates": {"valor": None, "fonte": None},
                "Exchange_Netflow": {"valor": None, "fonte": None},
                "Long_Short_Ratio": {"valor": None, "fonte": None}
            },
            "status": "no_data",
            "fonte_dados": "PostgreSQL"
        }