#app/services/ciclo/mvrv_z_score.py

from app.services.utils.indicadores_helper import is_indicator_outdated, force_update_indicator


INDICADOR = "MVRV_Z"

def get_dado_mvrv():
    """
    Retorna os dados do indicador MVRV_Z.
    Se estiver desatualizado (> 8h), força atualização antes.
    """
    if is_indicator_outdated(INDICADOR):
        return force_update_indicator(INDICADOR)
    
    # MOCK: retorno simulado do banco de dados
    return {
        "nome": INDICADOR,
        "valor": 2.1,
        "score": 6.0,
        "last_update": "2025-05-26T12:00:00Z"
    }

def calcular_score_mvrv():
    """
    Wrapper principal chamado no bloco ciclo.
    Utiliza get_dado_mvrv() que garante atualização automática.
    """
    dado = get_dado_mvrv()
    return {
        "valor": dado["valor"],
        "score": dado["score"]
    }
