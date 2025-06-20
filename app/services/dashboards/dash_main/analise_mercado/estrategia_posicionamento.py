# source: app/services/dashboards/dash_main/analise_mercado/estrategia_posicionamento.py

import logging

logger = logging.getLogger(__name__)

def definir_estrategia(ciclo: dict) -> dict:
    """
    Define estratégia de posicionamento baseada no ciclo identificado
    
    Returns:
        dict: Estratégia com posicionamento, tamanho, alavancagem, urgência
    """
    
    nome_ciclo = ciclo["nome"]
    estrategia_base = ESTRATEGIAS.get(nome_ciclo, ESTRATEGIAS["NEUTRO"])
    
    return {
        **estrategia_base,
        "ciclo_base": nome_ciclo,
        "confianca_ciclo": ciclo.get("confianca", 50)
    }

# Matriz de estratégias por ciclo
ESTRATEGIAS = {
    "CAPITULAÇÃO": {
        "posicionamento": "COMPRA_MAXIMA",
        "tamanho_posicao": "50-75%",
        "alavancagem_sugerida": "3.0x",
        "urgencia": "extrema",
        "descricao": "Oportunidade histórica de acumulação"
    },
    
    "BEAR PROFUNDO": {
        "posicionamento": "ACUMULAR",
        "tamanho_posicao": "30-40%", 
        "alavancagem_sugerida": "2.5x",
        "urgencia": "alta",
        "descricao": "DCA agressivo em território de valor"
    },
    
    "RECUPERAÇÃO": {
        "posicionamento": "DCA_CONSERVADOR",
        "tamanho_posicao": "20-30%",
        "alavancagem_sugerida": "2.0x", 
        "urgencia": "media",
        "descricao": "Entradas graduais conforme recuperação"
    },
    
    "ACUMULAÇÃO": {
        "posicionamento": "ENTRADAS_PEQUENAS",
        "tamanho_posicao": "10-20%",
        "alavancagem_sugerida": "2.0x",
        "urgencia": "baixa",
        "descricao": "Acumulação paciente em lateralização"
    },
    
    "NEUTRO": {
        "posicionamento": "AGUARDAR", 
        "tamanho_posicao": "10-15%",
        "alavancagem_sugerida": "1.5x",
        "urgencia": "baixa",
        "descricao": "Aguardar sinais direcionais claros"
    },
    
    "NEUTRO ALTA": {
        "posicionamento": "POSICAO_BASE",
        "tamanho_posicao": "15-25%",
        "alavancagem_sugerida": "1.8x",
        "urgencia": "baixa",
        "descricao": "Manter exposição básica com viés alta"
    },
    
    "SAÍDA ACUMULAÇÃO": {
        "posicionamento": "POSICAO_COMPLETA",
        "tamanho_posicao": "30-40%",
        "alavancagem_sugerida": "2.2x",
        "urgencia": "media",
        "descricao": "Completar posicionamento antes do bull"
    },
    
    "BULL INICIAL": {
        "posicionamento": "COMPRAR_RALLIES",
        "tamanho_posicao": "25-35%",
        "alavancagem_sugerida": "2.5x",
        "urgencia": "media",
        "descricao": "Participar de rompimentos e rallies"
    },
    
    "NOVO CICLO": {
        "posicionamento": "ALAVANCAGEM_MAXIMA",
        "tamanho_posicao": "40-60%",
        "alavancagem_sugerida": "3.0x",
        "urgencia": "alta",
        "descricao": "Aproveitar início de novo ciclo bull"
    },
    
    "BULL CONFIRMADO": {
        "posicionamento": "HOLD_E_COMPRAR_DIPS",
        "tamanho_posicao": "20-30%", 
        "alavancagem_sugerida": "2.0x",
        "urgencia": "media",
        "descricao": "Hold com compras em correções"
    },
    
    "OPORTUNIDADE GERACIONAL": {
        "posicionamento": "ALL_IN_ALAVANCAGEM",
        "tamanho_posicao": "60-80%",
        "alavancagem_sugerida": "3.0x",
        "urgencia": "extrema",
        "descricao": "Oportunidade única - máxima exposição"
    },
    
    "BULL FORTE": {
        "posicionamento": "HOLD_COM_STOPS",
        "tamanho_posicao": "10-20%",
        "alavancagem_sugerida": "1.5x",
        "urgencia": "baixa",
        "descricao": "Hold com proteções e stops"
    },
    
    "CORREÇÃO BULL": {
        "posicionamento": "COMPRAR_CORRECAO",
        "tamanho_posicao": "20-30%",
        "alavancagem_sugerida": "2.2x",
        "urgencia": "media",
        "descricao": "Aproveitar pullbacks em tendência bull"
    },
    
    "BULL TARDIO": {
        "posicionamento": "REALIZAR_GRADUAL",
        "tamanho_posicao": "REDUZIR_20-30%",
        "alavancagem_sugerida": "1.5x",
        "urgencia": "media",
        "descricao": "Começar realizações parciais"
    },
    
    "REVERSÃO ÉPICA": {
        "posicionamento": "COMPRA_MAXIMA",
        "tamanho_posicao": "70-90%",
        "alavancagem_sugerida": "3.0x",
        "urgencia": "extrema",
        "descricao": "V-bottom - oportunidade única"
    },
    
    "EUFORIA": {
        "posicionamento": "REALIZAR_LUCROS",
        "tamanho_posicao": "REDUZIR_50-80%",
        "alavancagem_sugerida": "1.0x",
        "urgencia": "alta",
        "descricao": "Realizar lucros em euforia"
    },
    
    "DISTRIBUIÇÃO": {
        "posicionamento": "REALIZAR_MAJORITARIO",
        "tamanho_posicao": "REDUZIR_60-80%",
        "alavancagem_sugerida": "0.5x",
        "urgencia": "alta",
        "descricao": "Smart money saindo - seguir"
    },
    
    "TOPO MANIA": {
        "posicionamento": "SAIR_POSICAO",
        "tamanho_posicao": "REDUZIR_80-100%", 
        "alavancagem_sugerida": "0x",
        "urgencia": "extrema",
        "descricao": "Sair completamente - topo formado"
    }
}

def get_urgencia_nivel(urgencia: str) -> int:
    """Converte urgência para nível numérico (1-4)"""
    niveis = {
        "baixa": 1,
        "media": 2, 
        "alta": 3,
        "extrema": 4
    }
    return niveis.get(urgencia, 2)

def get_tamanho_numerico(tamanho_str: str) -> float:
    """Extrai valor médio do tamanho da posição"""
    try:
        if "REDUZIR" in tamanho_str:
            return 0.0  # Sinaliza redução
        
        # Extrair números (ex: "25-35%" -> 30%)
        import re
        numeros = re.findall(r'\d+', tamanho_str)
        if len(numeros) >= 2:
            return (int(numeros[0]) + int(numeros[1])) / 2
        elif len(numeros) == 1:
            return int(numeros[0])
        else:
            return 15.0  # Default
            
    except Exception:
        return 15.0

def get_alavancagem_numerica(alav_str: str) -> float:
    """Extrai valor numérico da alavancagem"""
    try:
        import re
        numeros = re.findall(r'\d+\.?\d*', alav_str)
        if numeros:
            return float(numeros[0])
        else:
            return 1.0
    except Exception:
        return 1.0