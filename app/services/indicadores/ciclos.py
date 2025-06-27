# app/services/indicadores/ciclos.py

from datetime import datetime
from app.services.utils.helpers.postgres import get_dados_ciclo

def obter_indicadores():
    
    dados_db = get_dados_ciclo()
    
    if dados_db:
        return {
            "bloco": "ciclo",
            "status": "success",
            "timestamp": dados_db["timestamp"].isoformat() if dados_db["timestamp"] else datetime.utcnow().isoformat(),
            "indicadores": {
                "MVRV_Z": float(dados_db["mvrv_z_score"]) if dados_db["mvrv_z_score"] else 0.0,
                "Realized_Ratio": float(dados_db["realized_ratio"]) if dados_db["realized_ratio"] else 0.0,
                "Puell_Multiple": float(dados_db["puell_multiple"]) if dados_db["puell_multiple"] else 0.0,
                "NUPL": float(dados_db["nupl"]) if dados_db["nupl"] else 0.0,
                "Reserve_Risk": float(dados_db["reserve_risk"]) if dados_db["reserve_risk"]else 0.0
            }
        }
    else:
        return {
            "bloco": "ciclo",
            "status": "no_data",
            "timestamp": datetime.utcnow().isoformat(),
            "indicadores": {
                "MVRV_Z": 0 ,
                "Realized_Ratio": 0,
                "Puell_Multiple": 0,
                "NUPL": 0
            }
        }