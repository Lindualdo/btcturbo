# app/services/scores/momentum.py

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

def calcular_netflow_score(valor):
    """Calcula score Exchange Netflow - valor numérico (BTC)"""
    if valor < -50000:
        return 9.5, "ótimo"
    elif valor < -10000:
        return 7.5, "bom"
    elif valor < 10000:
        return 5.5, "neutro"
    elif valor < 50000:
        return 3.5, "ruim"
    else:
        return 1.5, "crítico"

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
    """Calcula score consolidado do bloco MOMENTUM v1.0.12"""
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
    netflow_valor = indicadores["Exchange_Netflow"]["valor"]
    ls_valor = indicadores["Long_Short_Ratio"]["valor"]
    
    rsi_score, rsi_classificacao = calcular_rsi_score(rsi_valor)
    funding_score, funding_classificacao = calcular_funding_score(funding_valor)
    netflow_score, netflow_classificacao = calcular_netflow_score(netflow_valor)
    ls_score, ls_classificacao = calcular_ls_ratio_score(ls_valor)
    
    # 3. Aplicar pesos NOVOS v1.0.12:
    # RSI: 12%, Funding: 10%, Netflow: 5%, L/S: 3% do total 30%
    # Normalizando para o bloco: RSI: 40%, Funding: 33.33%, Netflow: 16.67%, L/S: 10%
    score_consolidado = (
        (rsi_score * 0.40) +        # 12% / 30% = 40%
        (funding_score * 0.3333) +  # 10% / 30% = 33.33%
        (netflow_score * 0.1667) +  # 5% / 30% = 16.67%
        (ls_score * 0.10)           # 3% / 30% = 10%
    )
    
    # 4. Retornar JSON formatado
    return {
        "bloco": "momentum",
        "peso_bloco": "30%",
        "score_consolidado": round(score_consolidado, 2),
        "classificacao_consolidada": interpretar_classificacao_consolidada(score_consolidado),
        "timestamp": dados_indicadores["timestamp"],
        "indicadores": {
            "RSI_Semanal": {
                "valor": rsi_valor,
                "score": round(rsi_score, 1),
                "classificacao": rsi_classificacao,
                "peso": "12%",
                "fonte": indicadores["RSI_Semanal"]["fonte"]
            },
            "Funding_Rates": {
                "valor": funding_valor,
                "score": round(funding_score, 1),
                "classificacao": funding_classificacao,
                "peso": "10%",
                "fonte": indicadores["Funding_Rates"]["fonte"]
            },
            "Exchange_Netflow": {
                "valor": netflow_valor,
                "score": round(netflow_score, 1),
                "classificacao": netflow_classificacao,
                "peso": "5%",
                "fonte": indicadores["Exchange_Netflow"]["fonte"]
            },
            "Long_Short_Ratio": {
                "valor": ls_valor,
                "score": round(ls_score, 1),
                "classificacao": ls_classificacao,
                "peso": "3%",
                "fonte": indicadores["Long_Short_Ratio"]["fonte"]
            }
        },
        "status": "success"
    }