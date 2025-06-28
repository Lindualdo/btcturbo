# app/services/scores/tecnico_v3/utils/expansao_total_calculator.py

import logging

logger = logging.getLogger(__name__)

def calcular_expansao_total(ema_17: float, ema_610: float, timeframe: str) -> dict:
    """
    Calcula penalidade Expansão Total (40% do peso)
    Fórmula: (EMA17 / EMA610 - 1) × 100
    """
    try:
        if ema_610 == 0:
            return {"penalidade": 60, "expansao_pct": 0, "faixa": "erro"}
        
        expansao_pct = ((ema_17 / ema_610) - 1) * 100
        
        # Limites por timeframe
        if timeframe == "semanal":
            limites = [
                (50, 0),    # < 50%: 0 pontos
                (100, 20),  # 50-100%: -20 pontos
                (150, 40),  # 100-150%: -40 pontos
                (float('inf'), 60)  # > 150%: -60 pontos
            ]
        else:  # diário
            limites = [
                (30, 0),    # < 30%: 0 pontos
                (60, 20),   # 30-60%: -20 pontos
                (90, 40),   # 60-90%: -40 pontos
                (float('inf'), 60)  # > 90%: -60 pontos
            ]
        
        # Determinar penalidade
        penalidade = 0
        faixa = "verde"
        
        for limite, pts in limites:
            if expansao_pct < limite:
                penalidade = pts
                if pts == 0:
                    faixa = "verde"
                elif pts <= 20:
                    faixa = "amarelo"
                else:
                    faixa = "vermelho"
                break
        
        logger.info(f"📊 Expansão Total {timeframe}: {expansao_pct:.1f}% → -{penalidade}pts")
        
        return {
            "penalidade": penalidade,
            "expansao_pct": round(expansao_pct, 2),
            "faixa": faixa,
            "peso": 0.4
        }
        
    except Exception as e:
        logger.error(f"❌ Erro expansão total: {str(e)}")
        return {"penalidade": 60, "expansao_pct": 0, "faixa": "erro"}