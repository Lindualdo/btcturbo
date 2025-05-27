# app/services/indicadores/tecnico.py

from datetime import datetime
from app.services.utils.helpers.postgres import get_dados_tecnico

def obter_indicadores():
    dados_db = get_dados_tecnico()
    
    if dados_db:
        sistema_emas_score = float(dados_db["sistema_emas"]) if dados_db["sistema_emas"] else 0.0
        padroes_score = float(dados_db["padroes_graficos"]) if dados_db["padroes_graficos"] else 0.0
        
        # Interpretar scores
        if sistema_emas_score >= 8.0:
            emas_status = "Bullish Forte"
        elif sistema_emas_score >= 6.0:
            emas_status = "Bullish Moderado"
        elif sistema_emas_score >= 4.0:
            emas_status = "Neutro/Lateral"
        elif sistema_emas_score >= 2.0:
            emas_status = "Bearish Moderado"
        else:
            emas_status = "Bearish Forte"
        
        if padroes_score >= 7.0:
            padrao_status = "Bull Flag/Ascending Triangle"
        elif padroes_score >= 5.0:
            padrao_status = "Neutro/Sem Padrão"
        elif padroes_score >= 3.0:
            padrao_status = "Bear Flag/Descending Triangle"
        else:
            padrao_status = "Head & Shoulders/Double Top"
        
        return {
            "bloco": "tecnico",
            "timestamp": dados_db["timestamp"].isoformat() if dados_db["timestamp"] else datetime.utcnow().isoformat(),
            "indicadores": {
                "Sistema_EMAs": {
                    "valor": emas_status,
                    "score_numerico": sistema_emas_score,
                    "fonte": dados_db["fonte"] or "PostgreSQL"
                },
                "Padroes_Graficos": {
                    "valor": padrao_status,
                    "score_numerico": padroes_score,
                    "fonte": dados_db["fonte"] or "PostgreSQL"
                }
            },
            "status": "success",
            "fonte_dados": "PostgreSQL"
        }
    else:
        return {
            "bloco": "tecnico",
            "timestamp": datetime.utcnow().isoformat(),
            "indicadores": {
                "Sistema_EMAs": {"valor": None, "fonte": None},
                "Padroes_Graficos": {"valor": None, "fonte": None}
            },
            "status": "no_data",
            "fonte_dados": "PostgreSQL"
        }