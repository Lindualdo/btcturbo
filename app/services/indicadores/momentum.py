# app/services/indicadores/momentum.py

from datetime import datetime
from app.services.utils.helpers.postgres import get_dados_momentum

def obter_indicadores():
    """
    Retorna indicadores do bloco MOMENTUM incluindo SOPR v5.1.3
    ATUALIZADO: Substitui Exchange_Netflow por SOPR na resposta da API
    """
    dados_db = get_dados_momentum()
    
    if dados_db:
       
        return {
            "bloco": "momentum",
            "status": "success",
            "timestamp": dados_db["timestamp"].isoformat() if dados_db["timestamp"] else datetime.utcnow().isoformat(),
            "indicadores": {
                # Indicadores existentes (sem alteração)
                "RSI_Semanal":float(dados_db["rsi_semanal"]) if dados_db["rsi_semanal"] else 0.0,
                "Funding_Rates":f"{float(dados_db['funding_rates']):.5f}%" if dados_db["funding_rates"] else "0.00000%",
                "Long_Short_Ratio": float(dados_db["long_short_ratio"]) if dados_db["long_short_ratio"] else 0.0,
                "SOPR": float(dados_db["sopr"]) if dados_db["sopr"] else 0.0
            }
        }
    else:
        return {
            "bloco": "momentum",
            "status": "no_data",
            "timestamp": datetime.utcnow().isoformat(),
            "indicadores": {
                "RSI_Semanal": 0,
                "Funding_Rates": 0,
                "Long_Short_Ratio": 0,
                "SOPR": 0
            }
        }