# app/services/scores/tecnico.py

from app.services.indicadores import tecnico_v3 as indicadores_tecnico

def calcular_score():
    """O calculo do score é feito na hora da coleta, busca do tradingview e grava já calculado
        aqui apenas buscamos usando a função obter indicadore (usada pela api obter-indicxindicadores)   """
    # 1. Obter dados brutos da API
    return indicadores_tecnico.obter_indicadores()