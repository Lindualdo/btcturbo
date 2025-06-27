# app/services/scores/momentum.py - v5.1.3 COM SOPR

from app.services.indicadores import momentum as indicadores_momentum

def calcular_rsi_score(valor):
    """Calcula score RSI Semanal"""
    if valor < 30:
        return 9.5, "ótimo"
    elif valor < 45:
        return 7.5, "bom"
    elif valor < 55:
        return 5.5, "neutro"
    elif valor < 70:
        return 3.5, "ruim"
    else:
        return 1.5, "crítico"

def calcular_funding_score(valor_percentual):
    """Calcula score Funding Rates - valor já vem formatado como string"""
    # Converter string "X.XXX%" para float
    valor = float(valor_percentual.replace('%', '')) / 100
    
    if valor < -0.05:
        return 9.5, "ótimo"
    elif valor < 0:
        return 7.5, "bom"
    elif valor < 0.02:
        return 5.5, "neutro"
    elif valor < 0.1:
        return 3.5, "ruim"
    else:
        return 1.5, "crítico"

def calcular_sopr_score(valor):
    """
    NOVA FUNÇÃO v5.1.3: Calcula score SOPR (Spent Output Profit Ratio)
    Baseado na tabela de conversão do README v5.1.3
    
    Regras SOPR conforme especificação:
    - < 0.90: Score 10 (Capitulação Extrema)
    - 0.90-0.93: Score 9 (Capitulação Forte)
    - 0.93-0.95: Score 8 (Capitulação)
    - 0.95-0.97: Score 7 (Pressão Alta)
    - 0.97-0.99: Score 6 (Pressão Moderada)
    - 0.99-1.01: Score 5 (Neutro)
    - 1.01-1.02: Score 4 (Realização Leve)
    - 1.02-1.03: Score 3 (Realização Moderada)
    - 1.03-1.05: Score 2 (Realização Alta)
    - 1.05-1.08: Score 1 (Ganância)
    - > 1.08: Score 0 (Ganância Extrema)
    
    Args:
        valor: Valor SOPR (float)
        
    Returns:
        tuple: (score, classificacao)
    """
    if valor is None:
        return 5.0, "neutro"  # Score neutro quando SOPR não disponível
    
    try:
        valor_float = float(valor)
        
        # Aplicar tabela de conversão conforme README
        if valor_float < 0.90:
            return 10.0, "ótimo"  # Capitulação extrema - oportunidade máxima
        elif valor_float < 0.93:
            return 9.0, "ótimo"   # Capitulação forte
        elif valor_float < 0.95:
            return 8.0, "bom"     # Capitulação
        elif valor_float < 0.97:
            return 7.0, "bom"     # Pressão alta
        elif valor_float < 0.99:
            return 6.0, "bom"     # Pressão moderada
        elif valor_float <= 1.01:
            return 5.0, "neutro"  # Neutro/equilíbrio
        elif valor_float < 1.02:
            return 4.0, "ruim"    # Realização leve
        elif valor_float < 1.03:
            return 3.0, "ruim"    # Realização moderada
        elif valor_float < 1.05:
            return 2.0, "ruim"    # Realização alta
        elif valor_float < 1.08:
            return 1.0, "crítico" # Ganância
        else:
            return 0.0, "crítico" # Ganância extrema - topo local
            
    except (ValueError, TypeError):
        return 5.0, "neutro"  # Fallback para valores inválidos

def calcular_ls_ratio_score(valor):
    """Calcula score Long/Short Ratio"""
    if valor < 0.8:
        return 9.5, "ótimo"
    elif valor < 0.95:
        return 7.5, "bom"
    elif valor < 1.05:
        return 5.5, "neutro"
    elif valor < 1.3:
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
    """
    Calcula score consolidado do bloco MOMENTUM v5.1.3
    PESOS REBALANCEADOS: RSI 40% + Funding 35% + SOPR 15% + L/S 10% = 100%
    (SOPR substitui Exchange_Netflow mantendo o peso de 15%)
    """
    # 1. Obter dados brutos da API
    dados_indicadores = indicadores_momentum.obter_indicadores()
    
    if dados_indicadores.get("status") != "success":
        return {
            "bloco": "momentum",
            "status": "error",
            "erro": "Dados não disponíveis",
            "versao": "5.1.3"
        }
    
    indicadores = dados_indicadores["indicadores"]
    
  
    rsi_valor = indicadores["RSI_Semanal"]
    funding_valor = indicadores["Funding_Rates"]
    sopr_valor = indicadores["SOPR"]
    ls_valor = indicadores["Long_Short_Ratio"]
    
    rsi_score, rsi_classificacao = calcular_rsi_score(rsi_valor)
    funding_score, funding_classificacao = calcular_funding_score(funding_valor)
    sopr_score, sopr_classificacao = calcular_sopr_score(sopr_valor)  
    ls_score, ls_classificacao = calcular_ls_ratio_score(ls_valor)

    score_consolidado = (
        (rsi_score * 0.40) +        
        (funding_score * 0.35) +  
        (sopr_score * 0.15) +      
        (ls_score * 0.10)         
    )
    
    # 6. Retornar JSON formatado v5.1.3
    return {
        "status": "success",
        "bloco": "momentum",
        "peso_bloco": "20%",
        "score_consolidado": round(score_consolidado * 10, 1),
        "classificacao_consolidada": interpretar_classificacao_consolidada(score_consolidado),
        "timestamp": dados_indicadores["timestamp"],
        "indicadores": {
            "RSI_Semanal": {
                "valor": rsi_valor,
                "score": round(rsi_score * 10, 1)
            },
            "Funding_Rates": {
                "valor": funding_valor,
                "score": round(funding_score * 10, 1)
            },
            "SOPR": {
                "valor": sopr_valor,
                "score": round(sopr_score * 10, 1)
            },
            "Long_Short_Ratio": {
                "valor": ls_valor,
                "score": round(ls_score * 10, 1)
            }
        }
    }