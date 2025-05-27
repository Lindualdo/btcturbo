#app/services/utils/helper.py

from datetime import datetime, timedelta

# MOCK: banco de dados simulado
INDICADORES_MOCK = {
    "MVRV_Z": {"last_update": datetime.utcnow()},
    "RSI_Semanal": {"last_update": datetime.utcnow() - timedelta(hours=9)},
}

UPDATE_THRESHOLD_HOURS = 8

def is_indicator_outdated(nome: str) -> bool:
    """
    Verifica se o indicador está desatualizado (last_update > 8h)
    """
    indicador = INDICADORES_MOCK.get(nome)
    if not indicador:
        return True  # se não existir, forçar update
    last_update = indicador["last_update"]
    return (datetime.utcnow() - last_update).total_seconds() > UPDATE_THRESHOLD_HOURS * 3600


def force_update_indicator(nome: str) -> dict:
    """
    Função mock para forçar atualização do indicador e retornar novo valor
    (Simula o comportamento real futuro)
    """
    # Exemplo de retorno mock
    return {
        "nome": nome,
        "valor": 123.45,
        "score": 5.0,
        "last_update": datetime.utcnow().isoformat() + "Z"
    }
