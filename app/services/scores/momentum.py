# app/services/scores/momentum.py

from app.services.indicadores import momentum as indicadores_momentum

def calcular_rsi_score(valor):
    """Calcula score RSI Semanal"""
    if valor < 30:
        return 9.5  # Ótimo
    elif valor < 45:
        return 7.5  # Bom
    elif valor < 55:
        return 5.5  # Neutro
    elif valor < 70:
        return 3.5  # Ruim
    else:
        return 1.5  # Crítico

def calcular_funding_score(valor_percentual):
    """Calcula score Funding Rates - valor já vem formatado como string"""
    # Converter string "X.XXX%" para float
    valor = float(valor_percentual.replace('%', '')) / 100
    
    if valor < -0.05:
        return 9.5  # Ótimo
    elif valor < 0:
        return 7.5  # Bom
    elif valor < 0.02:
        return 5.5  # Neutro
    elif valor < 0.1:
        return 3.5  # Ruim
    else:
        return 1.5  # Crítico

def calcular_oi_score(valor_percentual):
    """Calcula score OI Change - valor já vem formatado como string"""
    # Converter string "+X.X%" ou "-X.X%" para float
    valor = float(valor_percentual.replace('%', '').replace('+', ''))
    
    if valor < -30:
        return 9.5  # Ótimo
    elif valor < -10:
        return 7.5  # Bom
    elif valor < 20:
        return 5.5  # Neutro
    elif valor < 50:
        return 3.5  # Ruim
    else:
        return 1.5  # Crítico

def calcular_ls_ratio_score(valor):
    """Calcula score Long/Short Ratio"""
    if valor < 0.8:
        return 9.5  # Ótimo
    elif valor < 0.95:
        return 7.5  # Bom
    elif valor < 1.05:
        return 5.5  # Neutro
    elif valor < 1.3:
        return 3.5  # Ruim
    else:
        return 1.5  # Crítico

def calcular_score():
    """Calcula score consolidado do bloco MOMENTUM"""
    # 1. Obter dados brutos da API
    dados_indicadores = indicadores_momentum.obter_indicadores()
    
    if dados_indicadores.get("status") != "success":
        return {
            "bloco": "momentum",
            "status": "error",
            "erro": "Dados não disponíveis"
        }
    
    indicadores = dados_indicadores["indicadores"]
    
    # 2. Calcular scores individuais
    rsi_valor = indicadores["RSI_Semanal"]["valor"]
    funding_valor = indicadores["Funding_Rates"]["valor"]
    oi_valor = indicadores["OI_Change"]["valor"]
    ls_valor = indicadores["Long_Short_Ratio"]["valor"]
    
    rsi_score = calcular_rsi_score(rsi_valor)
    funding_score = calcular_funding_score(funding_valor)
    oi_score = calcular_oi_score(oi_valor)
    ls_score = calcular_ls_ratio_score(ls_valor)
    
    # 3. Aplicar pesos (RSI: 10%, Funding: 8%, OI: 4%, L/S: 3% do total 25%)
    # Normalizando para o bloco: RSI: 40%, Funding: 32%, OI: 16%, L/S: 12%
    score_consolidado = (
        (rsi_score * 0.40) +
        (funding_score * 0.32) +
        (oi_score * 0.16) +
        (ls_score * 0.12)
    )
    
    # 4. Retornar JSON formatado
    return {
        "bloco": "momentum",
        "peso_bloco": "25%",
        "score_consolidado": round(score_consolidado, 2),
        "timestamp": dados_indicadores["timestamp"],
        "indicadores": {
            "RSI_Semanal": {
                "valor": rsi_valor,
                "score": round(rsi_score, 1),
                "peso": "10%",
                "fonte": indicadores["RSI_Semanal"]["fonte"]
            },
            "Funding_Rates": {
                "valor": funding_valor,
                "score": round(funding_score, 1),
                "peso": "8%",
                "fonte": indicadores["Funding_Rates"]["fonte"]
            },
            "OI_Change": {
                "valor": oi_valor,
                "score": round(oi_score, 1),
                "peso": "4%",
                "fonte": indicadores["OI_Change"]["fonte"]
            },
            "Long_Short_Ratio": {
                "valor": ls_valor,
                "score": round(ls_score, 1),
                "peso": "3%",
                "fonte": indicadores["Long_Short_Ratio"]["fonte"]
            }
        },
        "status": "success"
    }