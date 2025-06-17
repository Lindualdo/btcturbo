# services/v3/utils/analise/alavancagem/matriz_alavancagem.py
import logging

logger = logging.getLogger(__name__)

def calcular_limite_alavancagem(score_mercado: float, mvrv_zscore: float, ciclo_atual: str, 
                               rsi_mensal: float, health_factor: float) -> dict:
    """
    Matriz de Alavancagem - Calcula limite baseado em múltiplos fatores
    Conforme overview: Score Mercado + Indicadores Ciclo + IFR Mensal
    """
    try:
        logger.info("📊 Calculando limite de alavancagem...")
        
        # 1. Limite base por ciclo (MVRV-based conforme documentação V2)
        limite_base = _get_limite_por_ciclo(ciclo_atual, mvrv_zscore)
        
        # 2. Ajuste por score de mercado
        ajuste_mercado = _get_ajuste_score_mercado(score_mercado)
        
        # 3. Ajuste por RSI mensal (timing)
        ajuste_rsi = _get_ajuste_rsi_mensal(rsi_mensal)
        
        # 4. Ajuste por Health Factor (segurança)
        ajuste_hf = _get_ajuste_health_factor(health_factor)
        
        # 5. Limite final (aplicar todos os ajustes)
        limite_final = limite_base * ajuste_mercado * ajuste_rsi * ajuste_hf
        
        # 6. Garantir limites mínimo/máximo
        limite_final = max(1.0, min(3.0, limite_final))
        
        # 7. Gerar justificativa
        justificativa = _gerar_justificativa(
            limite_base, limite_final, ciclo_atual, score_mercado, rsi_mensal, health_factor
        )
        
        resultado = {
            "limite_alavancagem": round(limite_final, 1),
            "limite_base": limite_base,
            "ajustes": {
                "mercado": round(ajuste_mercado, 2),
                "rsi_mensal": round(ajuste_rsi, 2),
                "health_factor": round(ajuste_hf, 2)
            },
            "justificativa": justificativa,
            "fatores_utilizados": {
                "ciclo": ciclo_atual,
                "mvrv_zscore": mvrv_zscore,
                "score_mercado": score_mercado,
                "rsi_mensal": rsi_mensal,
                "health_factor": health_factor
            }
        }
        
        logger.info(f"✅ Limite calculado: {limite_final}x (base: {limite_base}x)")
        return resultado
        
    except Exception as e:
        logger.error(f"❌ Erro calcular limite: {str(e)}")
        return {
            "limite_alavancagem": 1.5,
            "limite_base": 1.5,
            "ajustes": {"mercado": 1.0, "rsi_mensal": 1.0, "health_factor": 1.0},
            "justificativa": f"Limite conservador devido a erro: {str(e)}",
            "fatores_utilizados": {}
        }

def _get_limite_por_ciclo(ciclo: str, mvrv_zscore: float) -> float:
    """
    Limite base por ciclo (conforme documentação V2)
    MVRV Z-Score define o ciclo e alavancagem máxima
    """
    # Primeira validação: MVRV Z-Score
    if mvrv_zscore >= 3.0:
        return 1.5  # EUFORIA_TOPO
    elif mvrv_zscore >= 2.0:
        return 2.0  # BULL_MADURO
    elif mvrv_zscore >= 1.0:
        return 2.5  # BULL_INICIAL
    elif mvrv_zscore >= 0:
        return 2.5  # ACUMULACAO
    else:
        return 3.0  # BOTTOM
    
    # Validação secundária por ciclo nomeado
    ciclo_limits = {
        "BOTTOM": 3.0,
        "ACUMULACAO": 2.5,
        "BULL_INICIAL": 2.5,
        "BULL_MADURO": 2.0,
        "EUFORIA_TOPO": 1.5
    }
    
    return ciclo_limits.get(ciclo, 2.0)

def _get_ajuste_score_mercado(score: float) -> float:
    """
    Ajuste baseado no score de mercado (0-100)
    Score alto = pode aumentar mais
    Score baixo = reduzir limite
    """
    if score >= 80:
        return 1.1  # +10%
    elif score >= 60:
        return 1.05  # +5%
    elif score >= 40:
        return 1.0  # Neutro
    elif score >= 20:
        return 0.9  # -10%
    else:
        return 0.8  # -20%

def _get_ajuste_rsi_mensal(rsi: float) -> float:
    """
    Ajuste baseado no RSI mensal (timing de entrada/saída)
    RSI baixo = pode aumentar (oversold)
    RSI alto = reduzir (overbought)
    """
    if rsi <= 30:
        return 1.15  # +15% (muito oversold)
    elif rsi <= 40:
        return 1.1   # +10% (oversold)
    elif rsi <= 60:
        return 1.0   # Neutro
    elif rsi <= 70:
        return 0.95  # -5% (overbought)
    else:
        return 0.85  # -15% (muito overbought)

def _get_ajuste_health_factor(hf: float) -> float:
    """
    Ajuste baseado no Health Factor (segurança da posição)
    HF alto = pode aumentar mais
    HF baixo = reduzir drasticamente
    """
    if hf >= 2.5:
        return 1.1   # +10% (muito seguro)
    elif hf >= 2.0:
        return 1.05  # +5% (seguro)
    elif hf >= 1.5:
        return 1.0   # Neutro
    elif hf >= 1.2:
        return 0.7   # -30% (arriscado)
    else:
        return 0.5   # -50% (muito arriscado)

def _gerar_justificativa(limite_base: float, limite_final: float, ciclo: str, 
                        score_mercado: float, rsi_mensal: float, hf: float) -> str:
    """
    Gera justificativa textual para o limite calculado
    """
    justificativas = []
    
    # Ciclo base
    justificativas.append(f"Ciclo {ciclo} permite base {limite_base}x")
    
    # Ajustes principais
    if score_mercado >= 70:
        justificativas.append(f"Score mercado alto ({score_mercado}) favorece aumento")
    elif score_mercado <= 30:
        justificativas.append(f"Score mercado baixo ({score_mercado}) reduz limite")
    
    if rsi_mensal <= 35:
        justificativas.append(f"RSI mensal baixo ({rsi_mensal}) permite mais alavancagem")
    elif rsi_mensal >= 65:
        justificativas.append(f"RSI mensal alto ({rsi_mensal}) reduz limite")
    
    if hf < 1.5:
        justificativas.append(f"Health Factor baixo ({hf}) limita alavancagem")
    elif hf > 2.0:
        justificativas.append(f"Health Factor seguro ({hf}) permite mais")
    
    # Resultado final
    if limite_final > limite_base:
        justificativas.append(f"Limite aumentado para {limite_final}x")
    elif limite_final < limite_base:
        justificativas.append(f"Limite reduzido para {limite_final}x por segurança")
    else:
        justificativas.append(f"Limite mantido em {limite_final}x")
    
    return ". ".join(justificativas) + "."