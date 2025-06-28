# app/services/scores/ciclos.py - v1.6.0 COM reserve_risk E PESOS REBALANCEADOS

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

def calcular_reserve_risk(valor):
    """Calcula score Reserve Risk baseado em faixas atualizadas - v1.6.0"""
    if valor < 0.002:
        return 9.5, "ótimo"
    elif valor < 0.005:
        return 7.5, "bom"
    elif valor < 0.01:
        return 5.5, "neutro"
    elif valor < 0.02:
        return 3.5, "ruim"
    else:
        return 1.0, "crítico"

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

def calcular_nupl_score(valor):
    """
    NOVA FUNÇÃO v5.1.2: Calcula score NUPL (Net Unrealized Profit/Loss)
    
    Regras NUPL conforme especificação v5.1.2:
    - < 0: Score 9-10 (Capitulação/Oversold extremo)
    - 0-0.25: Score 7-8 (Acumulação) 
    - 0.25-0.5: Score 5-6 (Neutro)
    - 0.5-0.75: Score 3-4 (Sobrecomprado/Otimismo)
    - > 0.75: Score 0-2 (Euforia/Topo)
    
    Args:
        valor: Valor NUPL (float)
        
    Returns:
        tuple: (score, classificacao)
    """
    if valor is None:
        return 5.5, "neutro"  # Score neutro quando NUPL não disponível
    
    try:
        valor_float = float(valor)
        
        if valor_float < 0:
            return 9.5, "ótimo"  # Capitulação - oportunidade máxima
        elif valor_float < 0.25:
            return 7.5, "bom"    # Acumulação - boa oportunidade
        elif valor_float < 0.5:
            return 5.5, "neutro" # Neutro - mercado equilibrado
        elif valor_float < 0.75:
            return 3.5, "ruim"   # Sobrecomprado - cautela
        else:
            return 1.5, "crítico" # Euforia - perigo extremo
            
    except (ValueError, TypeError):
        return 5.5, "neutro"  # Fallback para valores inválidos

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

    # 1. Obter dados brutos da API
    dados_indicadores = indicadores_ciclos.obter_indicadores()
    
    if dados_indicadores.get("status") != "success":
        return {
            "bloco": "ciclo",
            "status": "error",
            "erro": "Dados não disponíveis",
        }
    
    indicadores = dados_indicadores["indicadores"]
    
    # 2. Extrair valores individuais
    mvrv_valor = indicadores["MVRV_Z"]
    realized_valor = indicadores["Realized_Ratio"]
    nupl_valor = indicadores["NUPL"]
    reserve_risk_valor = indicadores["Reserve_Risk"]
    
    # 3. Calcular scores individuais
    mvrv_score, mvrv_classificacao = calcular_mvrv_score(mvrv_valor)
    realized_score, realized_classificacao = calcular_realized_score(realized_valor)
    nupl_score, nupl_classificacao = calcular_nupl_score(nupl_valor)  
    reserve_risk, nupl_classificacao = calcular_reserve_risk(reserve_risk_valor)  
    
    # 4. APLICAR PESOS REBALANCEADOS v1.6.0
    
    score_consolidado = (
        (mvrv_score * 0.40) +      # ← AUMENTADO: 50% → 30%  → 40
        (nupl_score * 0.20) +      # ← AUMENTADO: 20% → 30%
        (realized_score * 0.20) +  # ← REDUZIDO: 40% → 20%
        (reserve_risk * 0.10))    #  - NOVO
    
    # 6. Retornar JSON formatado

    """
        NUNCA ALTERAR ESSA ESTRUTURA NEM NOME DOS CAMPOS
        SE PRECISAR ALTERAR, ANALISAR GRAVÇÃO DOS DADOS (DASH-MERCADO E DASH-MAIN)
    """

    return {
        "bloco": "ciclo",
        "status": "success",
        "peso_bloco": "50%",  # Peso ajustado na v1.6.0 (era 40%)
        "score_consolidado": round(score_consolidado * 10, 1),
        "classificacao_consolidada": interpretar_classificacao_consolidada(score_consolidado),
        "timestamp": dados_indicadores["timestamp"],
        
        # INDICADORES COM PESOS REBALANCEADOS v1.6.0
        "indicadores": {
            "MVRV_Z": {
                "valor": mvrv_valor,
                "score": round(mvrv_score * 10, 1),
            },
            
            "NUPL": {
                "valor": nupl_valor,
                "score": round(nupl_score *10, 1),
            },
            
            "Realized_Ratio": {
                "valor": realized_valor,
                "score": round(realized_score * 10, 1),
            },
                        
            "Reserve_Risk": {
                "valor": reserve_risk_valor,
                "score": round(reserve_risk * 10, 1),
            }
        }
    }