# app/services/scores/tecnico_v3/utils/expansao_critica_calculator.py

import logging

logger = logging.getLogger(__name__)

def calcular_expansao_critica(ema_17: float, ema_144: float, timeframe: str) -> dict:
    """
    Calcula penalidade Expansão Crítica (40% do peso)
    Fórmula: (EMA17 / EMA144 - 1) × 100
    """
    try:
        if ema_144 == 0:
            return {"penalidade": 40, "expansao_pct": 0, "faixa": "erro"}
        
        expansao_pct = ((ema_17 / ema_144) - 1) * 100
        
        # Limites por timeframe
        if timeframe == "semanal":
            limites = [
                (10, 0),   # < 10%: 0 pontos
                (20, 15),  # 10-20%: -15 pontos
                (30, 30),  # 20-30%: -30 pontos
                (float('inf'), 40)  # > 30%: -40 pontos
            ]
        else:  # diário
            limites = [
                (6, 0),    # < 6%: 0 pontos
                (12, 15),  # 6-12%: -15 pontos
                (18, 30),  # 12-18%: -30 pontos
                (float('inf'), 40)  # > 18%: -40 pontos
            ]
        
        # Determinar penalidade
        penalidade = 0
        faixa = "verde"
        
        for limite, pts in limites:
            if expansao_pct < limite:
                penalidade = pts
                if pts == 0:
                    faixa = "verde"
                elif pts <= 15:
                    faixa = "amarelo"
                else:
                    faixa = "vermelho"
                break
        
        logger.info(f"🎯 Expansão Crítica {timeframe}: {expansao_pct:.1f}% → -{penalidade}pts")
        
        return {
            "penalidade": penalidade,
            "expansao_pct": round(expansao_pct, 2),
            "faixa": faixa,
            "peso": 0.4
        }
        
    except Exception as e:
        logger.error(f"❌ Erro expansão crítica: {str(e)}")
        return {"penalidade": 40, "expansao_pct": 0, "faixa": "erro"}