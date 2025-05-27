#/app/services/indicadores/tecnico.py

from datetime import datetime

def obter_indicadores():
    # TODO: Buscar do PostgreSQL via helper
    return {
        "bloco": "tecnico",
        "timestamp": datetime.utcnow().isoformat(),
        "indicadores": {
            "Sistema_EMAs": {"valor": "Bullish Alinhado", "fonte": "TradingView"},
            "Padroes_Graficos": {"valor": "Bull Flag", "fonte": "Manual"}
        }
    }