# app/services/scores/ciclos.py 

from app.services.indicadores import ciclos as indicadores_ciclos

def calcular_mvrv_score(valor):
    """Calcula score MVRV Z-Score baseado nos novos ranges"""
    if valor < 0:
        return 10
    elif valor < 1:
        return 8
    elif valor < 2:
        return 6
    elif valor < 3:
        return 4
    elif valor < 4:
        return 2
    else:  # valor >= 4
        return 0
    
def calcular_reserve_risk(valor):
    """Calcula score Reserve Risk baseado nos novos ranges"""
    if valor < 0.001:
        return 10
    elif valor < 0.0025:
        return 8
    elif valor < 0.005:
        return 6
    elif valor < 0.01:
        return 4
    elif valor < 0.02:
        return 2
    else:  # valor >= 0.02
        return 0

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
    """Calcula score Puell Multiple baseado nos novos ranges"""
    if valor < 0.5:
        return 10
    elif valor < 1:
        return 8
    elif valor < 1.5:
        return 6
    elif valor < 2.5:
        return 4
    elif valor < 4:
        return 2
    else:  # valor >= 4
        return 0

def calcular_nupl_score(valor):
    """Calcula score NUPL baseado nos novos ranges"""
    valor_float = float(valor)
    
    if valor_float < 0:
        return 10
    elif valor_float < 0.25:
        return 8
    elif valor_float < 0.5:
        return 6
    elif valor_float < 0.65:
        return 4
    elif valor_float < 0.75:
        return 2
    else:  # valor >= 0.75
        return 0

def interpretar_classificacao_consolidada(score):
    """Converte score consolidado em classificação estratégica"""
   
    
    if score >= 90:
        return "Oportunidade | Extremamente barato" #"Oportunidade Extrema | Extremamente barato"
    elif score >= 70:
        return "Valorização | abaixo do preço justo" #"Valorização | abaixo do preço justo"
    elif score >= 40:
        return "Equilíbrio | Valorização neutra" 
    elif score >= 20:
        return "Risco Elevado | Acima do preço justo"
    else:  # score <= 19
        return "Bolha | Euforia extrema"
    
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
    puell_valor = indicadores["Puell_Multiple"]
    
    # 3. Calcular scores individuais
    #realized_score, realized_classificacao = calcular_realized_score(realized_valor)
    mvrv_score, mvrv_classificacao = calcular_mvrv_score(mvrv_valor)
    nupl_score, nupl_classificacao = calcular_nupl_score(nupl_valor)  
    reserve_risk_score, nupl_classificacao = calcular_reserve_risk(reserve_risk_valor)  
    puell_score, nupl_classificacao = calcular_puell_score(puell_valor)  
    
    # 4.PESOS REBALANCEADOS v1.9
    score_consolidado = ( 
    (mvrv_score * 0.30) + 
    (nupl_score * 0.25) +   
    (reserve_risk_score * 0.35) +   
    (puell_score * 0.10))    
    
    # 6. Retornar JSON formatado

    """
        NUNCA ALTERAR ESSA ESTRUTURA NEM NOME DOS CAMPOS
        SE PRECISAR ALTERAR, ANALISAR GRAVÇÃO DOS DADOS (DASH-MERCADO E DASH-MAIN)
    """

    return {
        "bloco": "ciclo",
        "status": "success",
        "score_consolidado": round(score_consolidado * 10, 1),
        "classificacao_consolidada": interpretar_classificacao_consolidada(score_consolidado * 10),
        "timestamp": dados_indicadores["timestamp"],
        
        # INDICADORES COM PESOS REBALANCEADOS 
        "indicadores": {

            "mvrv_score": {
                "valor": mvrv_valor,
                "score": round(mvrv_score * 10, 1),
            },

            "NUPL": {
                "valor": nupl_valor,
                "score": round(nupl_score *10, 1),
            },
            
            "Reserve_Risk": {
                "valor": reserve_risk_valor,
                "score": round(reserve_risk_score * 10, 1),
            },

             "puell_multiple": {
                "valor": puell_valor,
                "score": round(puell_score * 10, 1)
            }
        }
    }