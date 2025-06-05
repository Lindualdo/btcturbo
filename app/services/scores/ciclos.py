# app/services/scores/ciclos.py

from app.services.indicadores import ciclos as indicadores_ciclos

def calcular_mvrv_score(valor):
    """Calcula score MVRV Z-Score baseado na tabela da documentação"""
    if valor < 0:
        return 9.5, "ótimo"
    elif valor < 2:
        return 7.5, "bom"
    elif valor < 4:
        return 5.5, "neutro"
    elif valor < 6:
        return 3.5, "ruim"
    else:
        return 1.5, "crítico"

def calcular_realized_score(valor):
    """Calcula score Realized Price Ratio"""
    if valor < 0.7:
        return 9.5, "ótimo"
    elif valor < 1.0:
        return 7.5, "bom"
    elif valor < 1.5:
        return 5.5, "neutro"
    elif valor < 2.5:
        return 3.5, "ruim"
    else:
        return 1.5, "crítico"

def calcular_puell_score(valor):
    """Calcula score Puell Multiple"""
    if valor < 0.5:
        return 9.5, "ótimo"
    elif valor < 1.0:
        return 7.5, "bom"
    elif valor < 2.0:
        return 5.5, "neutro"
    elif valor < 4.0:
        return 3.5, "ruim"
    else:
        return 1.5, "crítico"

def interpretar_classificacao_consolidada(score):
    """Converte score consolidado em classificação"""
    if score >= 8.0:
        return "ótimo"
    elif score >= 6.0:
        return "bom"
    elif score >= 4.0:
        return "neutro"
    elif score >= 2.0:
        return "ruim"
    else:
        return "crítico"

def calcular_score():
    """Calcula score consolidado do bloco CICLO"""
    # 1. Obter dados brutos da API
    dados_indicadores = indicadores_ciclos.obter_indicadores()
    
    if dados_indicadores.get("status") != "success":
        return {
            "bloco": "ciclo",
            "status": "error",
            "erro": "Dados não disponíveis"
        }
    
    indicadores = dados_indicadores["indicadores"]
    
    # 2. Calcular scores individuais
    mvrv_valor = indicadores["MVRV_Z"]["valor"]
    realized_valor = indicadores["Realized_Ratio"]["valor"]
    puell_valor = indicadores["Puell_Multiple"]["valor"]
    
    mvrv_score, mvrv_classificacao = calcular_mvrv_score(mvrv_valor)
    realized_score, realized_classificacao = calcular_realized_score(realized_valor)
    puell_score, puell_classificacao = calcular_puell_score(puell_valor)
    
    # 3. Aplicar pesos (MVRV: 50%, Realized: 40%, Puell: 10%)
    # NOTA: O do bloco é a soma do score ponderado de cada indicador
    score_consolidado = (
        (mvrv_score * 0.50) +
        (realized_score * 0.40) +
        (puell_score * 0.10)
    )
    
    # 4. Retornar JSON formatado
    return {
        "bloco": "ciclo",
        "peso": "50%",
        "score": round(score_consolidado, 2),
        "classificacao_consolidada": interpretar_classificacao_consolidada(score_consolidado),
        "timestamp": dados_indicadores["timestamp"],
        "indicadores": {
            "MVRV_Z": {
                "valor": mvrv_valor,
                "score": round(mvrv_score, 2),
                "score_consolidado": round(mvrv_score * 0.50, 2),
                "classificacao": mvrv_classificacao,
                "peso": "50%",
                "fonte": indicadores["MVRV_Z"]["fonte"]
            },
            "Realized_Ratio": {
                "valor": realized_valor,
                "score": round(realized_score, 2),
                "score_consolidado": round(realized_score * 0.40, 2),
                "classificacao": realized_classificacao,
                "peso": "40%",
                "fonte": indicadores["Realized_Ratio"]["fonte"]
            },
            "Puell_Multiple": {
                "valor": puell_valor,
                "score": round(puell_score, 2),
                "score_consolidado": round(puell_score * 0.10, 2),
                "classificacao": puell_classificacao,
                "peso": "10%",
                "fonte": indicadores["Puell_Multiple"]["fonte"]
            }
        },
        "status": "success"
    }