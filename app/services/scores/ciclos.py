#/app/services/coleta/ciclos.py

def calcular_score():
    # Simula cálculo com dados mockados
    return {
        "bloco": "ciclo",
        "score": 5.5,
        "indicadores": {
            "MVRV_Z": {"valor": 2.1, "score": 6.0},
            "Realized_Ratio": {"valor": 1.3, "score": 5.5},
            "Puell_Multiple": {"valor": 1.2, "score": 5.0}
        }
    }
