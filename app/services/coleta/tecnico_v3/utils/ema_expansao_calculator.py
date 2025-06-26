# app/services/scores/tecnico_v3/utils/ema_expansao_calculator.py

import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

def calcular_score_expansao(emas: Dict[str, float]) -> Dict:
    """
    Calcula Score Expansão baseado na v3.0
    
    Lógica: Inicia com 100 pontos, subtrai penalidades baseadas nas distâncias
    entre EMAs consecutivas. Quanto maior a distância, maior a penalidade.
    
    Tabela de Penalidades:
    - 17→34: Verde ≤3% | Amarelo 3.1-5% (-10pts) | Vermelho >5% (-25pts)
    - 34→144: Verde ≤8% | Amarelo 8.1-15% (-10pts) | Vermelho >15% (-25pts)  
    - 144→305: Verde ≤15% | Amarelo 15.1-25% (-10pts) | Vermelho >25% (-25pts)
    - 305→610: Verde ≤30% | Amarelo 30.1-50% (-10pts) | Vermelho >50% (-25pts)
    
    Args:
        emas: Dict com valores das EMAs {17: valor, 34: valor, ...}
        
    Returns:
        {
            "score": int (0-100),
            "penalidades": dict,
            "distancias": dict,
            "status": str
        }
    """
    try:
        logger.info("📐 Calculando Score Expansão v3.0...")
        
        # Validar EMAs obrigatórias
        emas_necessarias = [17, 34, 144, 305, 610]
        for ema in emas_necessarias:
            if ema not in emas or emas[ema] is None:
                raise ValueError(f"EMA {ema} não encontrada ou nula")
        
        score_inicial = 100
        penalidades_total = 0
        penalidades_detalhes = {}
        distancias = {}
        
        # Definir pares EMAs e suas faixas de penalidade
        pares_config = [
            {"menor": 17, "maior": 34, "verde": 3.0, "amarelo": 5.0},
            {"menor": 34, "maior": 144, "verde": 8.0, "amarelo": 15.0},
            {"menor": 144, "maior": 305, "verde": 15.0, "amarelo": 25.0},
            {"menor": 305, "maior": 610, "verde": 30.0, "amarelo": 50.0}
        ]
        
        # Calcular penalidades para cada par
        for config in pares_config:
            ema_menor = config["menor"]
            ema_maior = config["maior"]
            verde_limite = config["verde"]
            amarelo_limite = config["amarelo"]
            
            # Calcular distância percentual
            distancia_pct = _calcular_distancia_percentual(
                emas[ema_menor], emas[ema_maior]
            )
            
            par_nome = f"{ema_menor}_{ema_maior}"
            distancias[par_nome] = {
                "percentual": distancia_pct,
                "ema_menor": emas[ema_menor],
                "ema_maior": emas[ema_maior]
            }
            
            # Determinar penalidade baseada na faixa
            if distancia_pct <= verde_limite:
                # Verde: sem penalidade
                penalidade = 0
                cor = "verde"
            elif distancia_pct <= amarelo_limite:
                # Amarelo: -10 pontos
                penalidade = 10
                cor = "amarelo"
            else:
                # Vermelho: -25 pontos
                penalidade = 25
                cor = "vermelho"
            
            penalidades_total += penalidade
            penalidades_detalhes[par_nome] = {
                "distancia_pct": round(distancia_pct, 2),
                "penalidade": penalidade,
                "cor": cor,
                "faixa": f"Verde ≤{verde_limite}% | Amarelo ≤{amarelo_limite}% | Vermelho >{amarelo_limite}%"
            }
        
        # Score final = score inicial - penalidades
        score_final = max(0, score_inicial - penalidades_total)
        
        logger.info(f"✅ Score Expansão: {score_final}/100 (penalidades: -{penalidades_total})")
        
        return {
            "score": score_final,
            "score_inicial": score_inicial,
            "penalidades_total": penalidades_total,
            "penalidades": penalidades_detalhes,
            "distancias": distancias,
            "interpretacao": _interpretar_expansao(score_final),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro calcular expansão: {str(e)}")
        return {
            "score": 0,
            "penalidades_total": 0,
            "penalidades": {},
            "distancias": {},
            "interpretacao": "erro",
            "status": "error",
            "erro": str(e)
        }

def _calcular_distancia_percentual(ema_menor: float, ema_maior: float) -> float:
    """
    Calcula distância percentual entre EMAs
    
    Fórmula: ((EMA_menor - EMA_maior) / EMA_maior) × 100
    
    Resultado positivo = EMA menor está acima da maior (expansão)
    Resultado negativo = EMA menor está abaixo da maior (compressão)
    """
    if ema_maior == 0:
        return 0.0
        
    distancia = ((ema_menor - ema_maior) / ema_maior) * 100
    return abs(distancia)  # Usar valor absoluto para penalidades

def _interpretar_expansao(score: int) -> Dict:
    """Interpreta score de expansão"""
    if score >= 90:
        return {
            "classificacao": "EMAs Bem Compactadas",
            "descricao": "Estrutura saudável, baixa dispersão",
            "nivel": "excelente"
        }
    elif score >= 70:
        return {
            "classificacao": "Expansão Moderada",
            "descricao": "Algumas EMAs afastadas, mas controlado",
            "nivel": "bom"
        }
    elif score >= 50:
        return {
            "classificacao": "Expansão Significativa",
            "descricao": "EMAs bastante dispersas",
            "nivel": "alerta"
        }
    elif score >= 25:
        return {
            "classificacao": "Alta Dispersão",
            "descricao": "EMAs muito afastadas, risco de correção",
            "nivel": "cuidado"
        }
    else:
        return {
            "classificacao": "Dispersão Extrema",
            "descricao": "EMAs excessivamente afastadas",
            "nivel": "critico"
        }