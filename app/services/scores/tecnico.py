# app/services/scores/tecnico.py

from app.services.indicadores import tecnico as indicadores_tecnico

def calcular_emas_score(score_numerico):
    """Score já vem calculado do sistema EMAs - usar direto"""
    return score_numerico

def calcular_padroes_score(score_numerico):
    """Score já vem calculado dos padrões gráficos - usar direto"""
    return score_numerico

def interpretar_classificacao(score):
    """Converte score numérico em classificação"""
    if score >= 8.1:
        return "Tendência Forte"
    elif score >= 6.1:
        return "Correção Saudável"
    elif score >= 4.1:
        return "Neutro"
    elif score >= 2.1:
        return "Reversão"
    else:
        return "Bear Confirmado"

def calcular_score():
    """Calcula score consolidado do bloco TÉCNICO"""
    # 1. Obter dados brutos da API
    dados_indicadores = indicadores_tecnico.obter_indicadores()
    
    if dados_indicadores.get("status") != "success":
        return {
            "bloco": "tecnico",
            "status": "error",
            "erro": "Dados não disponíveis"
        }
    
    indicadores = dados_indicadores["indicadores"]
    
    # 2. Extrair scores já calculados
    emas_score_num = indicadores["Sistema_EMAs"]["score_numerico"]
    padroes_score_num = indicadores["Padroes_Graficos"]["score_numerico"]
    
    emas_score = calcular_emas_score(emas_score_num)
    padroes_score = calcular_padroes_score(padroes_score_num)
    
    # 3. Aplicar pesos (EMAs: 15%, Padrões: 5% do total 20%)
    # Normalizando para o bloco: EMAs: 75%, Padrões: 25%
    score_consolidado = (
        (emas_score * 0.75) +
        (padroes_score * 0.25)
    )
    
    # 4. Retornar JSON formatado
    return {
        "bloco": "tecnico",
        "peso_bloco": "20%",
        "score_consolidado": round(score_consolidado, 2),
        "classificacao": interpretar_classificacao(score_consolidado),
        "timestamp": dados_indicadores["timestamp"],
        "indicadores": {
            "Sistema_EMAs": {
                "valor": indicadores["Sistema_EMAs"]["valor"],
                "score": round(emas_score, 1),
                "peso": "15%",
                "fonte": indicadores["Sistema_EMAs"]["fonte"]
            },
            "Padroes_Graficos": {
                "valor": indicadores["Padroes_Graficos"]["valor"],
                "score": round(padroes_score, 1),
                "peso": "5%",
                "fonte": indicadores["Padroes_Graficos"]["fonte"]
            }
        },
        "status": "success"
    }