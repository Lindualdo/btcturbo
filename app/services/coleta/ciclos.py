#/app/services/coleta/ciclos.py

from datetime import datetime


def coletar(forcar_coleta: bool):
    # TODO: Implementar chamada real via helper (ex: from app.utils.helpers_ciclo import coletar_dados)
    
    status = "Dados coletados forçadamente" if forcar_coleta else "Dados coletados com cache"
    return {
        "bloco": "ciclos",
        "status": "sucesso",
        "timestamp": datetime.utcnow().isoformat(),
        "detalhes": status
    }
