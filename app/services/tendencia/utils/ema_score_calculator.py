# services/coleta/tendencia/utils/ema_score_calculator.py

import logging

logger = logging.getLogger(__name__)


def calculate_ema_score(current_price, emas):
 
    try:
        logger.info("📊 Calculando Bull Score EMAs...")
        
        # 1. Validar inputs obrigatórios
        required_emas = [10, 20, 50, 100, 200]
        for ema in required_emas:
            if ema not in emas or emas[ema] is None:
                raise ValueError(f"EMA {ema} não encontrada")
        
        if current_price is None or current_price <= 0:
            raise ValueError("Preço atual inválido")
        
        # 2. Calcular Bull Score
        bull_score = 0
        
        # Preço vs EMA10: ±10 pontos
        if current_price > emas[10]:
            bull_score += 10
        elif current_price < emas[10]:
            bull_score -= 10

        # EMA10 vs EMA20: ±15 pontos
        if emas[10] > emas[20]:
            bull_score += 15
        elif emas[10] < emas[20]:
            bull_score -= 15

        # EMA20 vs EMA50: ±20 pontos
        if emas[20] > emas[50]:
            bull_score += 20
        elif emas[20] < emas[50]:
            bull_score -= 20

        # EMA50 vs EMA100: ±25 pontos
        if emas[50] > emas[100]:
            bull_score += 25
        elif emas[50] < emas[100]:
            bull_score -= 25

        # EMA100 vs EMA200: ±30 pontos
        if emas[100] > emas[200]:
            bull_score += 30
        elif emas[100] < emas[200]:
            bull_score -= 30

        # 3. Normalizar para escala 0-100
        score_normalizado = max(0, min(100, int((bull_score + 100) / 2)))
        
        # 4. Log resultado
        logger.info(f"✅ Bull Score: {score_normalizado}/100")
        
        # 5. Retornar resultado
        return {
            "score": score_normalizado,
            "classificacao": _interpretar_alinhamento(score_normalizado),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro Bull Score: {str(e)}")
        return {
            "score": 0,
            "classificacao": "erro",
            "status": "error",
            "erro": str(e)
        }

def _interpretar_alinhamento(score: int) -> str:
    """Interpreta score 0-100 em classificação textual"""
    if score >= 88:
        return "Bull Aceleração"
    elif score >= 66:
        return "Bull Consolidação"
    elif score >= 35:
        return "Neutro/Transição"
    elif score >= 13:
        return "Bear Distribuição"
    else:
        return "Bear Capitulação"