# app/services/scores/ciclos.py 
import logging
from app.services.indicadores import ciclos as indicadores_ciclos

logger = logging.getLogger(__name__)

def calcular_mvrv_score(valor):
    """Calibrado para realidade pós-Out/21 (máximo ~4)"""
    if valor < 0:      return 10  # Crash/oportunidade extrema
    elif valor < 0.5:  return 9   # Muito subvalorizado
    elif valor < 1:    return 8   # Subvalorizado  
    elif valor < 1.5:  return 7   # Levemente subvalorizado
    elif valor < 2:    return 6   # Neutro baixo
    elif valor < 2.5:  return 5   # Neutro
    elif valor < 3:    return 4   # Neutro alto
    elif valor < 3.5:  return 2   # Sobrevalorizado
    elif valor < 4:    return 1   # Muito sobrevalorizado
    else:              return 0   # Extremo (raramente atingido)

def calcular_reserve_risk(valor):
    """
    Score Reserve Risk calibrado para mercado atual
    Range operacional: 0.001-0.01 (vs. 0.001-1.0 histórico)
    Score 10 = máxima oportunidade | Score 1 = máximo risco
    """
    if valor < 0.001:    return 10  # Oportunidade extrema (crash)
    elif valor < 0.0015: return 9   # Muito subvalorizado
    elif valor < 0.002:  return 8   # Subvalorizado forte  
    elif valor < 0.0025: return 7   # Subvalorizado
    elif valor < 0.003:  return 6   # Levemente subvalorizado
    elif valor < 0.004:  return 5   # Neutro baixo
    elif valor < 0.005:  return 4   # Neutro
    elif valor < 0.007:  return 3   # Neutro alto
    elif valor < 0.01:   return 2   # Sobrevalorizado (teto atual)
    else:                return 1   # Extremamente sobrevalorizado (>0.01)

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

    # 1 - Busca primeiro  o score combinando 
    resultado = calcular_score_combinado(indicadores)

    # 3. Calcular scores individuais
    #realized_score, realized_classificacao = calcular_realized_score(realized_valor)
    mvrv_score = calcular_mvrv_score(mvrv_valor)
    nupl_score = calcular_nupl_score(nupl_valor)  
    reserve_risk_score = calcular_reserve_risk(reserve_risk_valor)  
    puell_score = calcular_puell_score(puell_valor)  
    
    # 4.PESOS REBALANCEADOS v1.9
    score_consolidado = ( 
    (mvrv_score * 0.40) + 
    (nupl_score * 0.15) +   
    (reserve_risk_score * 0.35) +   
    (puell_score * 0.10))    
    
    tipo_score = "score_ponderado"
    # 6. Retornar JSON formatado

    """
        NUNCA ALTERAR ESSA ESTRUTURA NEM NOME DOS CAMPOS
        SE PRECISAR ALTERAR, ANALISAR GRAVÇÃO DOS DADOS (DASH-MERCADO E DASH-MAIN)
    """


  # Validar se retornou score combinado
    if resultado:
        score_consolidado = resultado["score_combinado"]
        logger.info(f"Score combinado: {score_consolidado}")
        tipo_score = "score_combinado"


    return {
        "bloco": "ciclo",
        "status": "success",
        "score_consolidado": round(score_consolidado * 10, 1),
        "classificacao_consolidada": interpretar_classificacao_consolidada(score_consolidado * 10),
        "timestamp": dados_indicadores["timestamp"],
        "tipo_score":  tipo_score,
        
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

def calcular_score_combinado(indicadores):
    
    
    # Extração dos valores
    mvrv_valor = float(indicadores["MVRV_Z"])
    nupl_valor = float(indicadores["NUPL"])
    reserve_risk_valor = float(indicadores["Reserve_Risk"])
    puell_valor = float(indicadores["Puell_Multiple"])
    
    # Condições em ordem decrescente de score (10 a 100)
    
    # Score 10: Condições extremas de alta
    if (mvrv_valor > 4.5 and 
        reserve_risk_valor > 0.012 and 
        nupl_valor > 0.65):
        return {"score_combinado": 10}
    
    # Score 20
    if (mvrv_valor > 3.8 and 
        puell_valor > 3 and 
        reserve_risk_valor > 0.01):
        return {"score_combinado": 20}
    
    # Score 30
    if (nupl_valor > 0.6 and 
        reserve_risk_valor > 0.008 and 
        mvrv_valor > 3.2):
        return {"score_combinado": 30}
    
    # Score 40
    if (mvrv_valor > 2.5 and 
        puell_valor > 2):
        return {"score_combinado": 40}
    
    # Score 50: Zona neutra
    if (0.3 <= nupl_valor <= 0.45 and 
        0.005 <= reserve_risk_valor <= 0.007):
        return {"score_combinado": 50}
    
    # Score 60
    if (1.2 <= mvrv_valor <= 2 and 
        0.004 <= reserve_risk_valor <= 0.005):
        return {"score_combinado": 60}
    
    # Score 70
    if (nupl_valor < 0.2 and 
        reserve_risk_valor < 0.004):
        return {"score_combinado": 70}
    
    # Score 80
    if (mvrv_valor < 1 and 
        puell_valor < 0.6 and 
        reserve_risk_valor < 0.003):
        return {"score_combinado": 80}
    
    # Score 90
    if (nupl_valor < 0.1 and 
        reserve_risk_valor < 0.002 and 
        puell_valor < 0.5):
        return {"score_combinado": 90}
    
    # Score 100: Condições extremas de baixa
    if (mvrv_valor < 0 and 
        nupl_valor < -0.15 and 
        reserve_risk_valor < 0.0015):
        return {"score_combinado": 100}
    
    # Nenhuma condição atendida
    return {}