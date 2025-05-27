# app/services/indicadores/riscos.py

from datetime import datetime
from app.services.utils.helpers.postgres import get_dados_risco

def obter_indicadores():
    dados_db = get_dados_risco()
    
    if dados_db:
        return {
            "bloco": "riscos",
            "timestamp": dados_db["timestamp"].isoformat() if dados_db["timestamp"] else datetime.utcnow().isoformat(),
            "indicadores": {
                "Dist_Liquidacao": {
                    "valor": f"{float(dados_db['dist_liquidacao']):.1f}%" if dados_db["dist_liquidacao"] else "0.0%",
                    "fonte": dados_db["fonte"] or "PostgreSQL"
                },
                "Health_Factor": {
                    "valor": float(dados_db["health_factor"]) if dados_db["health_factor"] else 0.0,
                    "fonte": dados_db["fonte"] or "PostgreSQL"
                },
                "Exchange_Netflow": {
                    "valor": f"{float(dados_db['exchange_netflow'])/1000:.0f}k" if dados_db["exchange_netflow"] else "0k",
                    "fonte": dados_db["fonte"] or "PostgreSQL"
                },
                "Stablecoin_Ratio": {
                    "valor": f"{float(dados_db['stablecoin_ratio']):.1f}%" if dados_db["stablecoin_ratio"] else "0.0%",
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
                "Health_Factor": {"valor": None, "fonte": None},
                "Exchange_Netflow": {"valor": None, "fonte": None},
                "Stablecoin_Ratio": {"valor": None, "fonte": None}
            },
            "status": "no_data",
            "fonte_dados": "PostgreSQL"
        }