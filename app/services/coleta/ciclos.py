#/app/services/coleta/ciclos.py

from datetime import datetime

def coletar(forcar_coleta):
    # Simula coleta mockada de indicadores externos
    if forcar_coleta:
        status = "Dados coletados forçadamente"
    else:
        status = "Dados coletados respeitando o cache"

    return {
        "bloco": "ciclo",
        "status": "sucesso",
        "timestamp": datetime.utcnow().isoformat(),
        "detalhes": status
    }
