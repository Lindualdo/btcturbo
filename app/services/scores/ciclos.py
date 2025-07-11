# app/services/scores/ciclos.py 
import logging
from app.services.indicadores import ciclos as indicadores_ciclos

logger = logging.getLogger(__name__)

def calcular_mvrv_score(valor):
    """MVRV calibrado (1=caro, 10=barato)"""
    if valor > 3.2:                return 1  # Extremamente caro
    elif 3.2 >= valor > 2.4:       return 2
    elif 2.4 >= valor > 2.0:       return 4
    elif 2.0 >= valor > 1.5:       return 6
    elif 1.5 >= valor > 1.0:       return 7     # Neutro
    elif 1.0 >= valor > 0.8:       return 9
    else:                          return 10  # Extremamente barato

def calcular_reserve_risk(rr_valor):
    #Reserve Risk ajustado - `Reserve Risk / SMA(Reserve Risk, 300)`

    if rr_valor >= 1.80: return 1       # Extremamente caro
    elif rr_valor >= 1.66: return 2
    elif rr_valor >= 1.51: return 3
    elif rr_valor >= 1.37: return 4
    elif rr_valor >= 1.22: return 5     # Neutro
    elif rr_valor >= 1.08: return 6
    elif rr_valor >= 0.93: return 7
    elif rr_valor >= 0.79: return 8
    elif rr_valor >= 0.60: return 9
    elif rr_valor <= 0.50: return 10   # Extremamente barato

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
    """NUPL calibrado conforme tabela (0=caro, 10=barato)"""
    valor_float = float(valor)
    
    if valor_float > 0.7:                        return 1   # Extremamente caro
    elif 0.65 <= valor_float <= 0.7:            return 2
    elif 0.6 <= valor_float < 0.65:             return 3
    elif 0.5 <= valor_float < 0.6:              return 4
    elif 0.35 <= valor_float < 0.5:             return 5   # Neutro
    elif 0.2 <= valor_float < 0.35:             return 6
    elif 0.05 <= valor_float < 0.2:             return 7
    elif -0.05 <= valor_float < 0.05:           return 8
    elif -0.15 <= valor_float < -0.05:          return 9
    else:                                       return 10  # Extremamente barato

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
    """Puell Multiple calibrado conforme tabela (0=caro, 10=barato)"""
    if valor > 3.5:               return 1   # Extremamente caro
    elif 3 <= valor <= 3.5:       return 2
    elif 2.5 <= valor < 3:        return 3
    elif 2 <= valor < 2.5:        return 4
    elif 1.3 <= valor < 2:        return 5   # Neutro
    elif 0.9 <= valor < 1.3:      return 6
    elif 0.6 <= valor < 0.9:      return 7
    elif 0.45 <= valor < 0.6:     return 8
    elif 0.35 <= valor < 0.45:    return 9
    else:                         return 10  # Extremamente barato

def interpretar_classificacao_consolidada(score):
    """Converte score consolidado em classificação estratégica
   
    - 0-20: Mercado muito caro (zona de distribuição)
    - 20-40: Mercado caro (cautela)
    - 40-60: Mercado neutro
    - 60-80: Mercado barato (acumulação)
    - 80-100: Mercado muito barato (forte acumulação)"""

    if score >= 90:
        return "Extremamente barato" #"Oportunidade Extrema | Extremamente barato"
    elif score >= 70:
        return "Abaixo do preço justo" #"Valorização | abaixo do preço justo"
    elif score >= 40:
        return "Valorização neutra" 
    elif score >= 20:
        return "Acima do preço justo"
    else:  # score <= 19
        return "Euforia extrema"
    
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
    #resultado = calcular_score_combinado_v2(indicadores)
    resultado = {}

    # 3. Calcular scores individuais
    #realized_score, realized_classificacao = calcular_realized_score(realized_valor)
    mvrv_score = calcular_mvrv_score(mvrv_valor)
    nupl_score = calcular_nupl_score(nupl_valor)  
    reserve_risk_score = calcular_reserve_risk(reserve_risk_valor)  
    puell_score = calcular_puell_score(puell_valor)  
    
    # 4.PESOS REBALANCEADOS v1.9
    score_consolidado = ( 
    (mvrv_score * 0.65) + 
    (nupl_score * 0.10) +   
    (reserve_risk_score * 0.15) +   
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
        logger.info(f"🚀 score combinado encontradoo...{score_consolidado}")

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

def calcular_score_combinado_v2(indicadores):
    """Score combinado usando apenas MVRV, NUPL e Reserve Risk
    Retorna score quando os 3 indicadores confirmam o mesmo nível"""
    
    mvrv_valor = float(indicadores["MVRV_Z"])
    nupl_valor = float(indicadores["NUPL"])
    reserve_risk_valor = float(indicadores["Reserve_Risk"])
    
    logger.info("🚀 iniciando score combinado v2...")
    
    # Score 1 (10): Extremamente caro - todos indicadores confirmam topo
    if (mvrv_valor >= 3.5 or 
        nupl_valor >= 0.65 or 
        reserve_risk_valor >= 1.70):
        return {"score_combinado": 1}
    
    # Score 2 (20): Muito caro
    if (mvrv_valor >= 3.2 or 
        nupl_valor >= 0.6 or 
        reserve_risk_valor >= 1.55):
        return {"score_combinado": 2}
    
    # Score 3 (30): Caro
    if (mvrv_valor >= 2.5 and 
        nupl_valor >= 0.5 and 
        reserve_risk_valor >= 1.40):
        return {"score_combinado": 3}
    
    # Score 4 (40): Levemente caro
    if (mvrv_valor >= 1.8 and 
        nupl_valor >= 0.35 and 
        reserve_risk_valor >= 1.25):
        return {"score_combinado": 4}
    
    # Score 5 (50): Neutro - zona de equilíbrio
    if (1.2 <= mvrv_valor <= 1.8 and 
        0.2 <= nupl_valor <= 0.35 and 
        1.10 <= reserve_risk_valor <= 1.25):
        return {"score_combinado": 5}
    
    # Score 6 (60): Levemente barato
    if (mvrv_valor <= 1.2 and 
        nupl_valor <= 0.2 and 
        reserve_risk_valor <= 1.10):
        return {"score_combinado": 6}
    
    # Score 7 (70): Barato
    if (mvrv_valor <= 0.8 and 
        nupl_valor <= 0.05 and 
        reserve_risk_valor <= 0.95):
        return {"score_combinado": 7}
    
    # Score 8 (80): Muito barato
    if (mvrv_valor <= 0.4 and 
        nupl_valor <= -0.05 and 
        reserve_risk_valor <= 0.80):
        return {"score_combinado": 8}
    
    # Score 9 (90): Extremamente barato
    if (mvrv_valor <= 0.0 and 
        nupl_valor <= -0.15 and 
        reserve_risk_valor <= 0.65):
        return {"score_combinado": 9}
    
    # Score 10 (100): Oportunidade máxima
    if (mvrv_valor <= -0.5 and 
        nupl_valor <= -0.20 and 
        reserve_risk_valor <= 0.50):
        return {"score_combinado": 10}
    
    logger.info("🚀 nenhum score combinado v2 encontrado...")
    return {}

def calcular_score_combinado(indicadores):
    
    
    # Extração dos valores
    mvrv_valor = float(indicadores["MVRV_Z"])
    nupl_valor = float(indicadores["NUPL"])
    reserve_risk_valor = float(indicadores["Reserve_Risk"])
    puell_valor = float(indicadores["Puell_Multiple"])
    
    # Condições em ordem decrescente de score (10 a 100)

    logger.info("🚀 iniciando o score combinado...")
    
    # Score 10: Condições extremas de alta
    if (mvrv_valor > 4 and 
        reserve_risk_valor > 2 and 
        nupl_valor > 0.6):
        return {"score_combinado": 1}
    
    # Score 20
    if (mvrv_valor > 3 and 
        reserve_risk_valor > 1.7):
        return {"score_combinado": 2}
    
    # Score 30
    if (nupl_valor >= 5 and 
        reserve_risk_valor >= 1.6 and 
        mvrv_valor >= 2.7):
        return {"score_combinado": 3}
    
    # Score 40
    if (mvrv_valor > 2.5 and 
        puell_valor > 2):
        return {"score_combinado": 4}
    
    # Score 50: Zona neutra
    if (0.3 <= nupl_valor <= 0.45 and 
        0.005 <= reserve_risk_valor <= 0.007):
        return {"score_combinado": 5}
    
    # Score 60
    if (1.2 <= mvrv_valor <= 2 and 
        0.004 <= reserve_risk_valor <= 0.005):
        return {"score_combinado": 6}
    
    # Score 70
    if (nupl_valor < 0.2 and 
        reserve_risk_valor < 0.004):
        return {"score_combinado": 7}
    
    # Score 80
    if (mvrv_valor < 1 and 
        puell_valor < 0.6 and 
        reserve_risk_valor < 0.003):
        return {"score_combinado": 8}
    
    # Score 90
    if (nupl_valor < 0.1 and 
        reserve_risk_valor < 0.002 and 
        puell_valor < 0.5):
        return {"score_combinado": 9}
    
    # Score 100: Condições extremas de baixa
    if (mvrv_valor < 0 and 
        nupl_valor < -0.15 and 
        reserve_risk_valor < 0.0015):
        return {"score_combinado": 10}
    
    logger.info("🚀 nenhum score combinado encontrado...")
    # Nenhuma condição atendida
    return {}