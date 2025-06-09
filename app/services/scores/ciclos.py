# app/services/scores/ciclos.py - v5.1.2 COM NUPL E PESOS REBALANCEADOS

from app.services.indicadores import ciclos as indicadores_ciclos

def calcular_mvrv_score(valor):
    """Calcula score MVRV Z-Score baseado na tabela da documentação"""
    if valor < 0:
        return 9.5, "ótimo"
    elif valor < 2:
        return 7.5, "bom"
    elif valor < 4:
        return 5.5, "neutro"
    elif valor < 6:
        return 3.5, "ruim"
    else:
        return 1.5, "crítico"

def calcular_realized_score(valor):
    """Calcula score Realized Price Ratio"""
    if valor < 0.7:
        return 9.5, "ótimo"
    elif valor < 1.0:
        return 7.5, "bom"
    elif valor < 1.5:
        return 5.5, "neutro"
    elif valor < 2.5:
        return 3.5, "ruim"
    else:
        return 1.5, "crítico"

def calcular_puell_score(valor):
    """Calcula score Puell Multiple"""
    if valor < 0.5:
        return 9.5, "ótimo"
    elif valor < 1.0:
        return 7.5, "bom"
    elif valor < 2.0:
        return 5.5, "neutro"
    elif valor < 4.0:
        return 3.5, "ruim"
    else:
        return 1.5, "crítico"

def calcular_nupl_score(valor):
    """
    NOVA FUNÇÃO v5.1.2: Calcula score NUPL (Net Unrealized Profit/Loss)
    
    Regras NUPL conforme especificação v5.1.2:
    - < 0: Score 9-10 (Capitulação/Oversold extremo)
    - 0-0.25: Score 7-8 (Acumulação) 
    - 0.25-0.5: Score 5-6 (Neutro)
    - 0.5-0.75: Score 3-4 (Sobrecomprado/Otimismo)
    - > 0.75: Score 0-2 (Euforia/Topo)
    
    Args:
        valor: Valor NUPL (float)
        
    Returns:
        tuple: (score, classificacao)
    """
    if valor is None:
        return 5.5, "neutro"  # Score neutro quando NUPL não disponível
    
    try:
        valor_float = float(valor)
        
        if valor_float < 0:
            return 9.5, "ótimo"  # Capitulação - oportunidade máxima
        elif valor_float < 0.25:
            return 7.5, "bom"    # Acumulação - boa oportunidade
        elif valor_float < 0.5:
            return 5.5, "neutro" # Neutro - mercado equilibrado
        elif valor_float < 0.75:
            return 3.5, "ruim"   # Sobrecomprado - cautela
        else:
            return 1.5, "crítico" # Euforia - perigo extremo
            
    except (ValueError, TypeError):
        return 5.5, "neutro"  # Fallback para valores inválidos

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
    Calcula score consolidado do bloco CICLO v5.1.2
    PESOS REBALANCEADOS: MVRV 30% + NUPL 20% + Realized 40% + Puell 10% = 100%
    """
    # 1. Obter dados brutos da API
    dados_indicadores = indicadores_ciclos.obter_indicadores()
    
    if dados_indicadores.get("status") != "success":
        return {
            "bloco": "ciclo",
            "status": "error",
            "erro": "Dados não disponíveis",
            "versao": "5.1.2"
        }
    
    indicadores = dados_indicadores["indicadores"]
    
    # 2. Extrair valores individuais
    mvrv_valor = indicadores["MVRV_Z"]["valor"]
    realized_valor = indicadores["Realized_Ratio"]["valor"]
    puell_valor = indicadores["Puell_Multiple"]["valor"]
    nupl_valor = indicadores["NUPL"]["valor"]  # ← NOVO v5.1.2
    
    # 3. Calcular scores individuais
    mvrv_score, mvrv_classificacao = calcular_mvrv_score(mvrv_valor)
    realized_score, realized_classificacao = calcular_realized_score(realized_valor)
    puell_score, puell_classificacao = calcular_puell_score(puell_valor)
    nupl_score, nupl_classificacao = calcular_nupl_score(nupl_valor)  # ← NOVO v5.1.2
    
    # 4. APLICAR PESOS REBALANCEADOS v5.1.2
    # ANTES: MVRV 50% + Realized 40% + Puell 10% = 100%
    # DEPOIS: MVRV 30% + NUPL 20% + Realized 40% + Puell 10% = 100%
    score_consolidado = (
        (mvrv_score * 0.30) +      # ← REDUZIDO: 50% → 30%
        (nupl_score * 0.20) +      # ← NOVO: 20%
        (realized_score * 0.40) +  # ← MANTÉM: 40%
        (puell_score * 0.10)       # ← MANTÉM: 10%
    )
    
    # 5. Determinar se NUPL está disponível para metadados
    nupl_disponivel = indicadores["NUPL"]["disponivel"]
    
    # 6. Retornar JSON formatado v5.1.2
    return {
        "bloco": "ciclo",
        "peso_bloco": "40%",  # Peso ajustado na v5.1.1 (era 50%)
        "score_consolidado": round(score_consolidado , 2),
        "score_consolidado_100": round(score_consolidado * 10, 1),  # ← NOVO: Base 100
        "classificacao_consolidada": interpretar_classificacao_consolidada(score_consolidado),
        "timestamp": dados_indicadores["timestamp"],
        "versao": "5.1.2",  # ← NOVO: Tracking de versão
        
        # INDICADORES COM PESOS REBALANCEADOS v5.1.2
        "indicadores": {
            "MVRV_Z": {
                "valor": mvrv_valor,
                "score": round(mvrv_score * 10, 1),
                "score_consolidado": round(mvrv_score * 0.30, 2),  # ← PESO REDUZIDO
                "classificacao": mvrv_classificacao,
                "peso": "30%",  # ← REDUZIDO: 50% → 30%
                "peso_anterior": "50%",  # ← METADADO: tracking mudança
                "fonte": indicadores["MVRV_Z"]["fonte"]
            },
            
            # NOVO INDICADOR v5.1.2: NUPL
            "NUPL": {
                "valor": nupl_valor,
                "score": round(nupl_score *10, 1),
                "score_consolidado": round(nupl_score * 0.20, 2),
                "classificacao": nupl_classificacao,
                "peso": "20%",  # ← NOVO: 20%
                "disponivel": nupl_disponivel,
                "fonte": indicadores["NUPL"]["fonte"],
                "versao_adicionado": "5.1.2",
                "observacao": "Novo indicador para melhor detecção de topos"
            },
            
            "Realized_Ratio": {
                "valor": realized_valor,
                "score": round(realized_score * 10, 1),
                "score_consolidado": round(realized_score * 0.40, 2),
                "classificacao": realized_classificacao,
                "peso": "40%",  # ← MANTÉM: 40%
                "fonte": indicadores["Realized_Ratio"]["fonte"]
            },
            
            "Puell_Multiple": {
                "valor": puell_valor,
                "score": round(puell_score * 10, 1),
                "score_consolidado": round(puell_score * 0.10, 2),
                "classificacao": puell_classificacao,
                "peso": "10%",  # ← MANTÉM: 10%
                "fonte": indicadores["Puell_Multiple"]["fonte"]
            }
        },
        
        # METADADOS REBALANCEAMENTO v5.1.2
        "rebalanceamento": {
            "versao_anterior": "5.1.1",
            "versao_atual": "5.1.2",
            "mudancas": [
                "MVRV Z-Score: 50% → 30% (reduzido)",
                "NUPL: 0% → 20% (novo indicador)",
                "Realized Ratio: 40% → 40% (mantido)",
                "Puell Multiple: 10% → 10% (mantido)"
            ],
            "justificativa": "NUPL mais responsivo em topos que MVRV Z-Score"
        },
        
        # FÓRMULA DE CÁLCULO v5.1.2
        "calculo": {
            "formula": "Score = (MVRV×0.30) + (NUPL×0.20) + (Realized×0.40) + (Puell×0.10)",
            "substituicao": f"Score = ({mvrv_score}×0.30) + ({nupl_score}×0.20) + ({realized_score}×0.40) + ({puell_score}×0.10)",
            "componentes": {
                "mvrv_contribuicao": round(mvrv_score * 0.30, 2),
                "nupl_contribuicao": round(nupl_score * 0.20, 2),
                "realized_contribuicao": round(realized_score * 0.40, 2),
                "puell_contribuicao": round(puell_score * 0.10, 2)
            },
            "total": round(score_consolidado, 2)
        },
        
        # ALERTAS ESPECÍFICOS v5.1.2
        "alertas": gerar_alertas_ciclo_v512(
            mvrv_valor, nupl_valor, realized_valor, puell_valor, nupl_disponivel
        ),
        
        "status": "success"
    }

def gerar_alertas_ciclo_v512(mvrv: float, nupl: float, realized: float, puell: float, nupl_disponivel: bool) -> list:
    """
    NOVA FUNÇÃO v5.1.2: Gera alertas específicos considerando NUPL
    """
    alertas = []
    
    try:
        # Alertas críticos NUPL
        if nupl_disponivel and nupl is not None:
            if nupl > 0.85:
                alertas.append("🚨 NUPL EXTREMO: Euforia máxima - vender agressivamente")
            elif nupl > 0.75:
                alertas.append("🔴 NUPL TOPO: Território perigoso - reduzir posições")
            elif nupl < 0:
                alertas.append("💎 NUPL NEGATIVO: Capitulação - oportunidade histórica")
        
        # Alertas MVRV (ajustados para novo peso)
        if mvrv > 5:
            alertas.append("📊 MVRV EXTREMO: Confirma sinais de topo")
        elif mvrv < 1:
            alertas.append("📊 MVRV BAIXO: Suporta acumulação")
        
        # Alertas contextuais (NUPL + MVRV)
        if nupl_disponivel and nupl is not None and mvrv is not None:
            if nupl > 0.75 and mvrv > 4:
                alertas.append("⚠️ DUPLA CONFIRMAÇÃO: NUPL + MVRV indicam topo")
            elif nupl < 0.25 and mvrv < 2:
                alertas.append("✅ DUPLA OPORTUNIDADE: NUPL + MVRV indicam acumulação")
        
        # Alerta ausência NUPL
        if not nupl_disponivel:
            alertas.append("⚠️ NUPL não disponível - usando apenas MVRV, Realized e Puell")
        
    except Exception as e:
        alertas.append(f"❌ Erro gerando alertas: {str(e)}")
    
    return alertas[:5]  # Máximo 5 alertas

def debug_scores_ciclo_nupl():
    """
    NOVA FUNÇÃO v5.1.2: Debug específico dos scores com NUPL
    """
    try:
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("🔍 DEBUG v5.1.2: Verificando scores CICLO com NUPL...")
        
        # Calcular score
        resultado = calcular_score()
        
        if resultado.get("status") == "success":
            logger.info("✅ Score calculado com sucesso")
            
            # Mostrar composição do score
            calculo = resultado.get("calculo", {})
            componentes = calculo.get("componentes", {})
            
            logger.info("📊 Composição do score v5.1.2:")
            logger.info(f"    MVRV (30%): {componentes.get('mvrv_contribuicao')}")
            logger.info(f"    NUPL (20%): {componentes.get('nupl_contribuicao')} ← NOVO")
            logger.info(f"    Realized (40%): {componentes.get('realized_contribuicao')}")
            logger.info(f"    Puell (10%): {componentes.get('puell_contribuicao')}")
            logger.info(f"    TOTAL: {componentes.get('total')}")
            
            # Verificar NUPL
            nupl_dados = resultado.get("indicadores", {}).get("NUPL", {})
            if nupl_dados.get("disponivel"):
                logger.info(f"📈 NUPL: {nupl_dados.get('valor')} - {nupl_dados.get('classificacao')}")
            else:
                logger.warning("⚠️ NUPL não disponível - usando pesos ajustados")
            
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