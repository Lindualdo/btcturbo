#/app/services/coleta/tecnico.py
from datetime import datetime

def coletar(forcar_coleta):
    # TODO: Implementar chamada real via helper (ex: from app.utils.helpers_ciclo import coletar_dados)

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
