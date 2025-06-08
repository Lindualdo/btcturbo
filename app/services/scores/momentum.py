# app/services/scores/momentum.py - v5.1.3 COM SOPR

from app.services.indicadores import momentum as indicadores_momentum

def calcular_rsi_score(valor):
    """Calcula score RSI Semanal"""
    if valor < 30:
        return 9.5, "ótimo"
    elif valor < 45:
        return 7.5, "bom"
    elif valor < 55:
        return 5.5, "neutro"
    elif valor < 70:
        return 3.5, "ruim"
    else:
        return 1.5, "crítico"

def calcular_funding_score(valor_percentual):
    """Calcula score Funding Rates - valor já vem formatado como string"""
    # Converter string "X.XXX%" para float
    valor = float(valor_percentual.replace('%', '')) / 100
    
    if valor < -0.05:
        return 9.5, "ótimo"
    elif valor < 0:
        return 7.5, "bom"
    elif valor < 0.02:
        return 5.5, "neutro"
    elif valor < 0.1:
        return 3.5, "ruim"
    else:
        return 1.5, "crítico"

def calcular_sopr_score(valor):
    """
    NOVA FUNÇÃO v5.1.3: Calcula score SOPR (Spent Output Profit Ratio)
    Baseado na tabela de conversão do README v5.1.3
    
    Regras SOPR conforme especificação:
    - < 0.90: Score 10 (Capitulação Extrema)
    - 0.90-0.93: Score 9 (Capitulação Forte)
    - 0.93-0.95: Score 8 (Capitulação)
    - 0.95-0.97: Score 7 (Pressão Alta)
    - 0.97-0.99: Score 6 (Pressão Moderada)
    - 0.99-1.01: Score 5 (Neutro)
    - 1.01-1.02: Score 4 (Realização Leve)
    - 1.02-1.03: Score 3 (Realização Moderada)
    - 1.03-1.05: Score 2 (Realização Alta)
    - 1.05-1.08: Score 1 (Ganância)
    - > 1.08: Score 0 (Ganância Extrema)
    
    Args:
        valor: Valor SOPR (float)
        
    Returns:
        tuple: (score, classificacao)
    """
    if valor is None:
        return 5.0, "neutro"  # Score neutro quando SOPR não disponível
    
    try:
        valor_float = float(valor)
        
        # Aplicar tabela de conversão conforme README
        if valor_float < 0.90:
            return 10.0, "ótimo"  # Capitulação extrema - oportunidade máxima
        elif valor_float < 0.93:
            return 9.0, "ótimo"   # Capitulação forte
        elif valor_float < 0.95:
            return 8.0, "bom"     # Capitulação
        elif valor_float < 0.97:
            return 7.0, "bom"     # Pressão alta
        elif valor_float < 0.99:
            return 6.0, "bom"     # Pressão moderada
        elif valor_float <= 1.01:
            return 5.0, "neutro"  # Neutro/equilíbrio
        elif valor_float < 1.02:
            return 4.0, "ruim"    # Realização leve
        elif valor_float < 1.03:
            return 3.0, "ruim"    # Realização moderada
        elif valor_float < 1.05:
            return 2.0, "ruim"    # Realização alta
        elif valor_float < 1.08:
            return 1.0, "crítico" # Ganância
        else:
            return 0.0, "crítico" # Ganância extrema - topo local
            
    except (ValueError, TypeError):
        return 5.0, "neutro"  # Fallback para valores inválidos

def calcular_ls_ratio_score(valor):
    """Calcula score Long/Short Ratio"""
    if valor < 0.8:
        return 9.5, "ótimo"
    elif valor < 0.95:
        return 7.5, "bom"
    elif valor < 1.05:
        return 5.5, "neutro"
    elif valor < 1.3:
        return 3.5, "ruim"
    else:
        return 1.5, "crítico"

def interpretar_classificacao_consolidada(score):
    """Converte score consolidado em classificação"""
    if score >= 8.0:
        return "ótimo"
    elif score >= 6.0:
        return "bom"
    elif score >= 4.0:
        return "neutro"
    elif score >= 2.0:
        return "ruim"
    else:
        return "crítico"

def calcular_score():
    """
    Calcula score consolidado do bloco MOMENTUM v5.1.3
    PESOS REBALANCEADOS: RSI 40% + Funding 35% + SOPR 15% + L/S 10% = 100%
    (SOPR substitui Exchange_Netflow mantendo o peso de 15%)
    """
    # 1. Obter dados brutos da API
    dados_indicadores = indicadores_momentum.obter_indicadores()
    
    if dados_indicadores.get("status") != "success":
        return {
            "bloco": "momentum",
            "status": "error",
            "erro": "Dados não disponíveis",
            "versao": "5.1.3"
        }
    
    indicadores = dados_indicadores["indicadores"]
    
    # 2. Extrair valores individuais v5.1.3
    rsi_valor = indicadores["RSI_Semanal"]["valor"]
    funding_valor = indicadores["Funding_Rates"]["valor"]
    sopr_valor = indicadores["SOPR"]["valor"]  # ← NOVO v5.1.3 (substitui Exchange_Netflow)
    ls_valor = indicadores["Long_Short_Ratio"]["valor"]
    
    # 3. Calcular scores individuais
    rsi_score, rsi_classificacao = calcular_rsi_score(rsi_valor)
    funding_score, funding_classificacao = calcular_funding_score(funding_valor)
    sopr_score, sopr_classificacao = calcular_sopr_score(sopr_valor)  # ← NOVO v5.1.3
    ls_score, ls_classificacao = calcular_ls_ratio_score(ls_valor)
    
    # 4. APLICAR PESOS v5.1.3 (SOPR substitui Exchange_Netflow)
    # RSI 40% + Funding_Rates 35% + SOPR 15% + Long_Short_Ratio 10% = 100%
    score_consolidado = (
        (rsi_score * 0.40) +        
        (funding_score * 0.35) +  
        (sopr_score * 0.15) +      # ← NOVO: SOPR com peso 15% (era Exchange_Netflow)
        (ls_score * 0.10)         
    )
    
    # 5. Determinar se SOPR está disponível para metadados
    sopr_disponivel = indicadores["SOPR"]["disponivel"]
    
    # 6. Retornar JSON formatado v5.1.3
    return {
        "bloco": "momentum",
        "peso_bloco": "20%",
        "score_consolidado": round(score_consolidado, 2),
        "classificacao_consolidada": interpretar_classificacao_consolidada(score_consolidado),
        "timestamp": dados_indicadores["timestamp"],
        "versao": "5.1.3",  # ← NOVO: Tracking de versão
        
        # INDICADORES COM SOPR v5.1.3
        "indicadores": {
            "RSI_Semanal": {
                "valor": rsi_valor,
                "score": round(rsi_score, 1),
                "score_consolidado": round(rsi_score * 0.40, 2),
                "classificacao": rsi_classificacao,
                "peso": "40%",
                "fonte": indicadores["RSI_Semanal"]["fonte"]
            },
            "Funding_Rates": {
                "valor": funding_valor,
                "score": round(funding_score, 1),
                "score_consolidado": round(funding_score * 0.35, 2),
                "classificacao": funding_classificacao,
                "peso": "35%",
                "fonte": indicadores["Funding_Rates"]["fonte"]
            },
            
            # NOVO INDICADOR v5.1.3: SOPR (substitui Exchange_Netflow)
            "SOPR": {
                "valor": sopr_valor,
                "score": round(sopr_score, 1),
                "score_consolidado": round(sopr_score * 0.15, 2),
                "classificacao": sopr_classificacao,
                "peso": "15%",  # ← MANTÉM peso de 15% (era Exchange_Netflow)
                "disponivel": sopr_disponivel,
                "fonte": indicadores["SOPR"]["fonte"],
                "versao_adicionado": "5.1.3",
                "substitui": "Exchange_Netflow",
                "observacao": "SOPR mais eficaz que Exchange Netflow para detectar capitulação/euforia"
            },
            
            "Long_Short_Ratio": {
                "valor": ls_valor,
                "score": round(ls_score, 1),
                "score_consolidado": round(ls_score * 0.10, 2),
                "classificacao": ls_classificacao,
                "peso": "10%",
                "fonte": indicadores["Long_Short_Ratio"]["fonte"]
            }
        },
        
        # METADADOS MUDANÇA v5.1.3
        "substituicao": {
            "versao_anterior": "5.1.2",
            "versao_atual": "5.1.3",
            "mudancas": [
                "Exchange_Netflow removido da API (mantido no DB para compatibilidade)",
                "SOPR adicionado com peso 15% (mesmo peso do Exchange_Netflow)",
                "Algoritmo SOPR baseado na tabela de conversão do README"
            ],
            "justificativa": "SOPR é mais eficaz para detectar capitulação e euforia que Exchange Netflow"
        },
        
        # FÓRMULA DE CÁLCULO v5.1.3
        "calculo": {
            "formula": "Score = (RSI×0.40) + (Funding×0.35) + (SOPR×0.15) + (L/S×0.10)",
            "substituicao": f"Score = ({rsi_score}×0.40) + ({funding_score}×0.35) + ({sopr_score}×0.15) + ({ls_score}×0.10)",
            "componentes": {
                "rsi_contribuicao": round(rsi_score * 0.40, 2),
                "funding_contribuicao": round(funding_score * 0.35, 2),
                "sopr_contribuicao": round(sopr_score * 0.15, 2),  # ← NOVO
                "ls_contribuicao": round(ls_score * 0.10, 2)
            },
            "total": round(score_consolidado, 2)
        },
        
        # ALERTAS ESPECÍFICOS v5.1.3
        "alertas": gerar_alertas_momentum_v513(
            rsi_valor, funding_valor, sopr_valor, ls_valor, sopr_disponivel
        ),
        
        "status": "success"
    }

def gerar_alertas_momentum_v513(rsi: float, funding: str, sopr: float, ls_ratio: float, sopr_disponivel: bool) -> list:
    """
    NOVA FUNÇÃO v5.1.3: Gera alertas específicos considerando SOPR
    """
    alertas = []
    
    try:
        # Alertas críticos SOPR
        if sopr_disponivel and sopr is not None:
            if sopr < 0.90:
                alertas.append("🔥 SOPR EXTREMO: Capitulação máxima detectada - oportunidade histórica")
            elif sopr < 0.95:
                alertas.append("💎 SOPR BAIXO: Capitulação ativa - considerar compras")
            elif sopr > 1.08:
                alertas.append("🚨 SOPR EXTREMO: Ganância máxima - considerar saídas")
            elif sopr > 1.05:
                alertas.append("🔴 SOPR ALTO: Realização excessiva - reduzir posições")
        
        # Alertas RSI (ajustados para contexto SOPR)
        if rsi < 30:
            if sopr_disponivel and sopr is not None and sopr < 0.95:
                alertas.append("💎 DUPLA CONFIRMAÇÃO: RSI + SOPR indicam fundo")
            else:
                alertas.append("📊 RSI OVERSOLD: Possível reversão de curto prazo")
        elif rsi > 70:
            if sopr_disponivel and sopr is not None and sopr > 1.05:
                alertas.append("🚨 DUPLA CONFIRMAÇÃO: RSI + SOPR indicam topo")
            else:
                alertas.append("📊 RSI OVERBOUGHT: Cautela recomendada")
        
        # Alertas Funding Rates
        try:
            funding_float = float(funding.replace('%', '')) / 100
            if funding_float > 0.05:
                alertas.append("💰 FUNDING ALTO: Longs pagando caro - possível correção")
            elif funding_float < -0.02:
                alertas.append("💰 FUNDING NEGATIVO: Shorts pagando - força bullish")
        except:
            pass
        
        # Alerta ausência SOPR
        if not sopr_disponivel:
            alertas.append("⚠️ SOPR não disponível - usando apenas RSI, Funding e L/S")
        
    except Exception as e:
        alertas.append(f"❌ Erro gerando alertas: {str(e)}")
    
    return alertas[:5]  # Máximo 5 alertas

def debug_scores_momentum_sopr():
    """
    NOVA FUNÇÃO v5.1.3: Debug específico dos scores com SOPR
    """
    try:
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("🔍 DEBUG v5.1.3: Verificando scores MOMENTUM com SOPR...")
        
        # Calcular score
        resultado = calcular_score()
        
        if resultado.get("status") == "success":
            logger.info("✅ Score calculado com sucesso")
            
            # Mostrar composição do score
            calculo = resultado.get("calculo", {})
            componentes = calculo.get("componentes", {})
            
            logger.info("📊 Composição do score v5.1.3:")
            logger.info(f"    RSI (40%): {componentes.get('rsi_contribuicao')}")
            logger.info(f"    Funding (35%): {componentes.get('funding_contribuicao')}")
            logger.info(f"    SOPR (15%): {componentes.get('sopr_contribuicao')} ← NOVO")
            logger.info(f"    L/S (10%): {componentes.get('ls_contribuicao')}")
            logger.info(f"    TOTAL: {componentes.get('total')}")
            
            # Verificar SOPR
            sopr_dados = resultado.get("indicadores", {}).get("SOPR", {})
            if sopr_dados.get("disponivel"):
                logger.info(f"📈 SOPR: {sopr_dados.get('valor')} - {sopr_dados.get('classificacao')}")
            else:
                logger.warning("⚠️ SOPR não disponível - usando pesos ajustados")
            
            # Mostrar alertas
            alertas = resultado.get("alertas", [])
            if alertas:
                logger.info("🚨 Alertas ativos:")
                for alerta in alertas:
                    logger.info(f"    - {alerta}")
            
            return resultado
        else:
            logger.error(f"❌ Erro no cálculo: {resultado.get('erro')}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro no debug: {str(e)}")
        return None

# FUNÇÃO LEGADA MANTIDA PARA COMPATIBILIDADE
def calcular_netflow_score(valor):
    """
    DEPRECATED v5.1.3: Função legada do Exchange Netflow
    Mantida para compatibilidade, mas não é mais usada no cálculo principal
    """
    import logging
    logging.warning("⚠️ calcular_netflow_score() está deprecated na v5.1.3 - foi substituída por calcular_sopr_score()")
    
    if valor < -50000:
        return 9.5, "ótimo"
    elif valor < -10000:
        return 7.5, "bom"
    elif valor < 10000:
        return 5.5, "neutro"
    elif valor < 50000:
        return 3.5, "ruim"
    else:
        return 1.5, "crítico"