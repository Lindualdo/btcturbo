# app/services/scores/riscos.py

from app.services.indicadores import riscos as indicadores_riscos

def calcular_dist_liquidacao_score(valor_percentual):
    """Calcula score Distância Liquidação - valor já vem formatado como string"""
    try:
        valor = float(valor_percentual.replace('%', ''))
    except (ValueError, AttributeError):
        return 5.5, "neutro"  # Fallback em caso de erro
    
    if valor > 50:
        return 9.5, "ótimo"
    elif valor > 30:
        return 7.5, "bom"
    elif valor > 20:
        return 5.5, "neutro"
    elif valor > 10:
        return 3.5, "ruim"
    else:
        return 1.5, "crítico"

def calcular_health_factor_score(valor):
    """Calcula score Health Factor AAVE"""
    try:
        valor = float(valor) if valor is not None else 0.0
    except (ValueError, TypeError):
        return 5.5, "neutro"  # Fallback em caso de erro
    
    if valor > 2.0:
        return 9.5, "ótimo"
    elif valor > 1.5:
        return 7.5, "bom"
    elif valor > 1.3:
        return 5.5, "neutro"
    elif valor > 1.1:
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
    """Calcula score consolidado do bloco RISCO"""
    # 1. Obter dados brutos da API
    dados_indicadores = indicadores_riscos.obter_indicadores()
    
    if dados_indicadores.get("status") != "success":
        return {
            "bloco": "riscos",
            "status": "error",
            "erro": "Dados não disponíveis"
        }
    
    indicadores = dados_indicadores["indicadores"]
    
    # 2. Calcular scores individuais
    dist_valor = indicadores["Dist_Liquidacao"]["valor"]
    hf_valor = indicadores["Health_Factor"]["valor"]
    
    dist_score, dist_classificacao = calcular_dist_liquidacao_score(dist_valor)
    hf_score, hf_classificacao = calcular_health_factor_score(hf_valor)
    
    # 3. Aplicar pesos (Dist: 5%, HF: 5% do total 10%)
    # Normalizando para o bloco: Dist: 50%, HF: 50%
    score_consolidado = (
        (dist_score * 0.50) +
        (hf_score * 0.50)
    )
    
    # 4. Retornar JSON formatado
    return {
        "bloco": "riscos",
        "peso_bloco": "10%",
        "score_consolidado": round(score_consolidado, 2),
        "classificacao_consolidada": interpretar_classificacao_consolidada(score_consolidado),
        "timestamp": dados_indicadores["timestamp"],
        "indicadores": {
            "Dist_Liquidacao": {
                "valor": dist_valor,
                "score": round(dist_score, 1),
                "classificacao": dist_classificacao,
                "peso": "5%",
                "fonte": indicadores["Dist_Liquidacao"]["fonte"]
            },
            "Health_Factor": {
                "valor": hf_valor,
                "score": round(hf_score, 1),
                "classificacao": hf_classificacao,
                "peso": "5%",
                "fonte": indicadores["Health_Factor"]["fonte"]
            }
        },
        "status": "success"
    }