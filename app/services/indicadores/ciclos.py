# app/services/indicadores/ciclos.py

from datetime import datetime
from app.services.utils.helpers.postgres import get_dados_ciclo

def obter_indicadores():
    dados_db = get_dados_ciclo()
    
    if dados_db:
        return {
            "bloco": "ciclo",
            "timestamp": dados_db["timestamp"].isoformat() if dados_db["timestamp"] else datetime.utcnow().isoformat(),
            "indicadores": {
                "MVRV_Z": {
                    "valor": float(dados_db["mvrv_z_score"]) if dados_db["mvrv_z_score"] else 0.0,
                    "fonte": dados_db["fonte"] or "PostgreSQL"
                },
                "Realized_Ratio": {
                    "valor": float(dados_db["realized_ratio"]) if dados_db["realized_ratio"] else 0.0,
                    "fonte": dados_db["fonte"] or "PostgreSQL"
                },
                "Puell_Multiple": {
                    "valor": float(dados_db["puell_multiple"]) if dados_db["puell_multiple"] else 0.0,
                    "fonte": dados_db["fonte"] or "PostgreSQL"
                }
            },
            "status": "success",
            "fonte_dados": "PostgreSQL"
        }
    else:
        return {
            "bloco": "ciclo",
            "timestamp": datetime.utcnow().isoformat(),
            "indicadores": {
                "MVRV_Z": {"valor": None, "fonte": None},
                "Realized_Ratio": {"valor": None, "fonte": None},
                "Puell_Multiple": {"valor": None, "fonte": None}
            },
            "status": "no_data",
            "fonte_dados": "PostgreSQL"
        }