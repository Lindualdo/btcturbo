# app/services/dashboards/dash_main/analise_mercado/matriz_ciclos.py
# Implementação correta da matriz de ciclos conforme 1.2-matriz-ciclo.md

import logging

logger = logging.getLogger(__name__)

def identificar_ciclo(score: float, mvrv: float, nupl: float) -> dict:
    """
    Identifica ciclo baseado na matriz de 18 cenários
    
    Aplica regras de prevalência:
    1. NUPL < 0 sempre zona de compra (override tudo)
    2. MVRV > 4 sempre zona de topo (override tudo exceto NUPL < 0)
    3. Score extremos (0-20 ou 90-100) prevalecem
    4. Verifica AMBOS MVRV e NUPL nas faixas definidas
    
    Args:
        score: Score de mercado (0-100)
        mvrv: MVRV Z-Score
        nupl: Net Unrealized Profit/Loss
    
    Returns:
        dict: Dados do ciclo identificado
    """
    
    # REGRA 1: NUPL < 0 - ZONA COMPRA EXTREMA (override tudo)
    if nupl < 0:
        return _ciclo_nupl_negativo(score)
    
    # REGRA 2: MVRV > 4 - ZONA TOPO (override exceto NUPL < 0)
    if mvrv > 4.0:
        return _ciclo_topo_mania()
    
    # REGRA 3: SCORES EXTREMOS (override faixas intermediárias)
    if score >= 90:
        return _ciclo_score_extremo_alto(mvrv, nupl)
    elif score <= 20:
        return _ciclo_score_extremo_baixo(mvrv, nupl)
    
    # MATRIZ NORMAL - verifica ambos MVRV e NUPL
    return _aplicar_matriz_definitiva(score, mvrv, nupl)

def _ciclo_nupl_negativo(score: float) -> dict:
    """REGRA 1: NUPL < 0 - zonas de compra histórica"""
    if score <= 20:
        return {
            "nome": "CAPITULAÇÃO",
            "caracteristicas": "Pânico total, fundos fechando",
            "estrategia": "All-in histórico",
            "confianca": 95,
            "override": "NUPL_NEGATIVO",
            "tamanho_posicao": "50-75%"
        }
    else:
        return {
            "nome": "BEAR PROFUNDO",
            "caracteristicas": "Desespero, mídia negativa", 
            "estrategia": "Acumular forte",
            "confianca": 90,
            "override": "NUPL_NEGATIVO",
            "tamanho_posicao": "30-40%"
        }

def _ciclo_topo_mania() -> dict:
    """REGRA 2: MVRV > 4 - zona de topo"""
    return {
        "nome": "TOPO MANIA",
        "caracteristicas": "Euforia extrema, notícias mainstream",
        "estrategia": "Sair 80-100%",
        "confianca": 95,
        "override": "MVRV_EXTREMO",
        "tamanho_posicao": "Realizar 60-80%"
    }

def _ciclo_score_extremo_alto(mvrv: float, nupl: float) -> dict:
    """REGRA 3: Score >= 90 - condições extremas positivas"""
    
    # 90-100 | <0.8 | <0 | REVERSÃO ÉPICA
    if mvrv < 0.8 and nupl < 0:
        return {
            "nome": "REVERSÃO ÉPICA",
            "caracteristicas": "V-bottom histórico",
            "estrategia": "Compra máxima", 
            "confianca": 95,
            "override": "SCORE_EXTREMO",
            "tamanho_posicao": "Compra máxima"
        }
    
    # 90-100 | >2.5 | >0.65 | EUFORIA
    elif mvrv > 2.5 and nupl > 0.65:
        return {
            "nome": "EUFORIA",
            "caracteristicas": "Parabólico, retail all-in",
            "estrategia": "Sair 50-80%",
            "confianca": 90,
            "override": "SCORE_EXTREMO",
            "tamanho_posicao": "Realizar 40-50%"
        }
    
    # Fallback para score extremo
    else:
        return {
            "nome": "SCORE_EXTREMO_INDEFINIDO",
            "caracteristicas": f"Score 90+ mas MVRV:{mvrv:.2f} NUPL:{nupl:.3f} fora matriz",
            "estrategia": "Aguardar clareza",
            "confianca": 60,
            "override": "SCORE_EXTREMO_INCOMPLETO"
        }

def _ciclo_score_extremo_baixo(mvrv: float, nupl: float) -> dict:
    """REGRA 3: Score <= 20 - condições extremas negativas"""
    
    # 0-20 | <1.0 | <0 | CAPITULAÇÃO
    if mvrv < 1.0 and nupl < 0:
        return {
            "nome": "CAPITULAÇÃO",
            "caracteristicas": "Pânico total, fundos fechando",
            "estrategia": "All-in histórico",
            "confianca": 90,
            "override": "SCORE_EXTREMO",
            "tamanho_posicao": "50-75%"
        }
    
    # 0-20 | >4.0 | >0.75 | TOPO MANIA
    elif mvrv > 4.0 and nupl > 0.75:
        return {
            "nome": "TOPO MANIA", 
            "caracteristicas": "Euforia extrema, notícias mainstream",
            "estrategia": "Sair 80-100%",
            "confianca": 85,
            "override": "SCORE_EXTREMO",
            "tamanho_posicao": "Realizar 60-80%"
        }
    
    # Fallback para score extremo baixo
    else:
        return {
            "nome": "SCORE_BAIXO_INDEFINIDO",
            "caracteristicas": f"Score ≤20 mas MVRV:{mvrv:.2f} NUPL:{nupl:.3f} fora matriz",
            "estrategia": "Aguardar clareza",
            "confianca": 60,
            "override": "SCORE_EXTREMO_INCOMPLETO"
        }

def _aplicar_matriz_definitiva(score: float, mvrv: float, nupl: float) -> dict:
    """
    Aplica matriz completa verificando AMBOS MVRV e NUPL
    
    Para cada faixa de score, verifica se MVRV E NUPL estão nas faixas definidas.
    Se não encontrar match exato, retorna o cenário mais próximo ou indefinido.
    """
    
    # Faixa 80-90
    if 80 <= score < 90:
        # 80-90 | 2.0-3.0 | 0.5-0.7 | BULL FORTE
        if 2.0 <= mvrv <= 3.0 and 0.5 <= nupl <= 0.7:
            return {
                "nome": "BULL FORTE",
                "caracteristicas": "Momentum poderoso, notícias positivas",
                "estrategia": "Hold + Stops",
                "confianca": 85,
                "tamanho_posicao": "10-20%"
            }
        
        # 80-90 | <1.0 | <0.1 | OPORTUNIDADE GERACIONAL
        elif mvrv < 1.0 and nupl < 0.1:
            return {
                "nome": "OPORTUNIDADE GERACIONAL",
                "caracteristicas": "Capitulação com reversão técnica",
                "estrategia": "All-in + Alavancagem",
                "confianca": 85,
                "tamanho_posicao": "Compra máxima"
            }
    
    # Faixa 70-80
    elif 70 <= score < 80:
        # 70-80 | 1.2-2.2 | 0.35-0.55 | BULL CONFIRMADO
        if 1.2 <= mvrv <= 2.2 and 0.35 <= nupl <= 0.55:
            return {
                "nome": "BULL CONFIRMADO",
                "caracteristicas": "Tendência clara, FOMO inicial",
                "estrategia": "Hold + Comprar dips",
                "confianca": 80,
                "tamanho_posicao": "20-30%"
            }
        
        # 70-80 | <1.2 | <0.25 | NOVO CICLO
        elif mvrv < 1.2 and nupl < 0.25:
            return {
                "nome": "NOVO CICLO",
                "caracteristicas": "Saindo de bear, reversão confirmada",
                "estrategia": "Alavancagem máxima",
                "confianca": 85,
                "tamanho_posicao": "Alavancagem máxima"
            }
    
    # Faixa 60-70
    elif 60 <= score < 70:
        # 60-70 | 1.5-2.5 | 0.3-0.5 | BULL INICIAL
        if 1.5 <= mvrv <= 2.5 and 0.3 <= nupl <= 0.5:
            return {
                "nome": "BULL INICIAL",
                "caracteristicas": "Rompimentos, otimismo crescente",
                "estrategia": "Comprar rallies",
                "confianca": 75,
                "tamanho_posicao": "25-35%"
            }
        
        # 60-70 | 1.0-1.8 | 0.2-0.35 | SAÍDA ACUMULAÇÃO
        elif 1.0 <= mvrv <= 1.8 and 0.2 <= nupl <= 0.35:
            return {
                "nome": "SAÍDA ACUMULAÇÃO",
                "caracteristicas": "Volume crescente, breakouts",
                "estrategia": "Posição completa",
                "confianca": 75,
                "tamanho_posicao": "25-35%"
            }
    
    # Faixa 50-60 (CASO ATUAL)
    elif 50 <= score < 60:
        # 50-60 | 1.8-2.5 | 0.35-0.5 | NEUTRO ALTA
        if 1.8 <= mvrv <= 2.5 and 0.35 <= nupl <= 0.5:
            return {
                "nome": "NEUTRO ALTA",
                "caracteristicas": "Indecisão com viés positivo",
                "estrategia": "Posição base",
                "confianca": 70,
                "tamanho_posicao": "10-15%"
            }
        
        # 50-60 | 1.5-2.2 | 0.25-0.4 | NEUTRO
        elif 1.5 <= mvrv <= 2.2 and 0.25 <= nupl <= 0.4:
            return {
                "nome": "NEUTRO",
                "caracteristicas": "Consolidação, baixa volatilidade",
                "estrategia": "Aguardar sinal",
                "confianca": 65,
                "tamanho_posicao": "10-15%"
            }
    
    # Faixa 40-50
    elif 40 <= score < 50:
        # 40-50 | 2.0-3.0 | 0.4-0.55 | CORREÇÃO BULL
        if 2.0 <= mvrv <= 3.0 and 0.4 <= nupl <= 0.55:
            return {
                "nome": "CORREÇÃO BULL",
                "caracteristicas": "Pullback em tendência alta",
                "estrategia": "Comprar correção",
                "confianca": 75,
                "tamanho_posicao": "20-30%"
            }
        
        # 40-50 | 1.2-2.0 | 0.1-0.35 | ACUMULAÇÃO
        elif 1.2 <= mvrv <= 2.0 and 0.1 <= nupl <= 0.35:
            return {
                "nome": "ACUMULAÇÃO",
                "caracteristicas": "Lateralização, volume baixo",
                "estrategia": "Pequenas entradas",
                "confianca": 70,
                "tamanho_posicao": "10-20%"
            }
    
    # Faixa 30-40
    elif 30 <= score < 40:
        # 30-40 | 2.5-3.5 | 0.5-0.65 | BULL TARDIO
        if 2.5 <= mvrv <= 3.5 and 0.5 <= nupl <= 0.65:
            return {
                "nome": "BULL TARDIO",
                "caracteristicas": "Ganância crescente, leverage alta",
                "estrategia": "Realizar gradual",
                "confianca": 75,
                "tamanho_posicao": "Realizar 20-30%"
            }
        
        # 30-40 | 1.0-1.5 | 0-0.25 | RECUPERAÇÃO
        elif 1.0 <= mvrv <= 1.5 and 0 <= nupl <= 0.25:
            return {
                "nome": "RECUPERAÇÃO",
                "caracteristicas": "Bear acabando, sentimento melhorando",
                "estrategia": "DCA conservador",
                "confianca": 70,
                "tamanho_posicao": "20-30%"
            }
    
    # Faixa 20-30
    elif 20 <= score < 30:
        # 20-30 | 3.0-4.0 | 0.6-0.75 | DISTRIBUIÇÃO
        if 3.0 <= mvrv <= 4.0 and 0.6 <= nupl <= 0.75:
            return {
                "nome": "DISTRIBUIÇÃO",
                "caracteristicas": "Smart money vendendo, retail comprando",
                "estrategia": "Realizar 60%+",
                "confianca": 80,
                "tamanho_posicao": "Realizar 60-80%"
            }
        
        # 20-30 | 0.8-1.2 | -0.1-0.1 | BEAR PROFUNDO
        elif 0.8 <= mvrv <= 1.2 and -0.1 <= nupl <= 0.1:
            return {
                "nome": "BEAR PROFUNDO",
                "caracteristicas": "Desespero, mídia negativa",
                "estrategia": "Acumular forte",
                "confianca": 75,
                "tamanho_posicao": "30-40%"
            }
    
    # FALLBACK: Nenhum cenário encontrado
    return _ciclo_indefinido(score, mvrv, nupl)

def _ciclo_indefinido(score: float, mvrv: float, nupl: float) -> dict:
    """
    Retorna quando nenhum cenário da matriz é encontrado
    
    Fornece diagnóstico do porque não foi possível identificar o ciclo
    """
    
    # Determinar qual indicador está mais fora das faixas
    diagnosticos = []
    
    if score < 20 or score > 100:
        diagnosticos.append(f"Score {score:.1f} fora do range válido")
    
    if mvrv < 0.5 or mvrv > 5.0:
        diagnosticos.append(f"MVRV {mvrv:.2f} em valor extremo")
    
    if nupl < -0.2 or nupl > 0.8:
        diagnosticos.append(f"NUPL {nupl:.3f} em valor extremo")
    
    diagnostico = " | ".join(diagnosticos) if diagnosticos else "Combinação não prevista na matriz"
    
    logger.info(f"🔍 Ciclo indefinido: {diagnostico}")
    
    return {
        "nome": "INDEFINIDO",
        "caracteristicas": f"Condições atípicas: {diagnostico}",
        "estrategia": "Aguardar clareza ou usar análise manual",
        "confianca": 30,
        "tamanho_posicao": "Conservador 5-10%"
    }