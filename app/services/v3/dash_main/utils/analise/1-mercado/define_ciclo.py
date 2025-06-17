# app/services/v3/dash_mercado/utils/define_ciclo.py

def collect_all_data_v3() -> dict:
    """
    busca o score de mercado e indicadores necessários para definir o ciclo de mercado
    
    """
    all_data = {
        "score_mercado": 56,
        "ciclo": "BULL MADURO",
        "size_position": 10
    }

    return all_data