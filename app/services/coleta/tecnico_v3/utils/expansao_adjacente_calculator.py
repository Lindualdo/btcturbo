# app/services/scores/tecnico_v3/utils/expansao_adjacente_calculator.py

import logging

logger = logging.getLogger(__name__)

def calcular_expansao_adjacente(emas: dict, timeframe: str) -> dict:
    """
    Calcula penalidade Expansão Adjacente (20% do peso)
    EMAs consecutivas com limites por timeframe
    """
    try:
        # Configuração por timeframe
        if timeframe == "semanal":
            pares_config = [
                {"menor": 17, "maior": 34, "verde": 3.0, "amarelo": 5.0},
                {"menor": 34, "maior": 144, "verde": 8.0, "amarelo": 15.0},
                {"menor": 144, "maior": 305, "verde": 15.0, "amarelo": 25.0},
                {"menor": 305, "maior": 610, "verde": 30.0, "amarelo": 50.0}
            ]
        else:  # diário
            pares_config = [
                {"menor": 17, "maior": 34, "verde": 2.0, "amarelo": 3.0},
                {"menor": 34, "maior": 144, "verde": 5.0, "amarelo": 10.0},
                {"menor": 144, "maior": 305, "verde": 10.0, "amarelo": 18.0},
                {"menor": 305, "maior": 610, "verde": 20.0, "amarelo": 35.0}
            ]
        
        penalidades_total = 0
        detalhes = {}
        
        for config in pares_config:
            ema_menor = config["menor"]
            ema_maior = config["maior"]
            verde_limite = config["verde"]
            amarelo_limite = config["amarelo"]
            
            # Calcular distância percentual
            if emas[ema_maior] == 0:
                distancia_pct = 0
            else:
                distancia_pct = abs(((emas[ema_menor] - emas[ema_maior]) / emas[ema_maior]) * 100)
            
            # Determinar penalidade
            if distancia_pct <= verde_limite:
                penalidade = 0
                cor = "verde"
            elif distancia_pct <= amarelo_limite:
                penalidade = 10
                cor = "amarelo"
            else:
                penalidade = 25
                cor = "vermelho"
            
            penalidades_total += penalidade
            par_nome = f"{ema_menor}_{ema_maior}"
            
            detalhes[par_nome] = {
                "distancia_pct": round(distancia_pct, 2),
                "penalidade": penalidade,
                "cor": cor
            }
        
        logger.info(f"🔗 Expansão Adjacente {timeframe}: -{penalidades_total}pts")
        
        return {
            "penalidade": penalidades_total,
            "detalhes": detalhes,
            "peso": 0.2
        }
        
    except Exception as e:
        logger.error(f"❌ Erro expansão adjacente: {str(e)}")
        return {"penalidade": 100, "detalhes": {}, "peso": 0.2}