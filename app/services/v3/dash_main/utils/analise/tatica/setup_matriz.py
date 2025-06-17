# services/v3/utils/analise/tatica/setup_matriz.py
import logging

logger = logging.getLogger(__name__)

def aplicar_matriz_decisao(ciclo: str, setup: str, mercado_data: dict, 
                          risco_data: dict, alavancagem_data: dict) -> dict:
    """
    Matriz de Decisão Final: Ciclo × Setup → Ação + Tamanho
    Conforme documentação V2
    """
    try:
        logger.info(f"🎯 Aplicando matriz: {ciclo} × {setup}")
        
        # 1. Buscar decisão base na matriz Ciclo × Setup
        decisao_base = _get_matriz_base_decisao(ciclo, setup)
        
        # 2. Aplicar ajustes por contexto (HF, alavancagem, etc)
        decisao_ajustada = _aplicar_ajustes_contexto(
            decisao_base, risco_data, alavancagem_data, mercado_data
        )
        
        # 3. Filtros de emergência
        decisao_final = _aplicar_filtros_emergencia(
            decisao_ajustada, risco_data["health_factor"], 
            alavancagem_data["capital_livre_percent"]
        )
        
        # 4. Validação final
        decisao_validada = _validar_decisao_final(decisao_final)
        
        logger.info(f"✅ Matriz aplicada: {decisao_validada['decisao']} {decisao_validada['tamanho_percent']}%")
        return decisao_validada
        
    except Exception as e:
        logger.error(f"❌ Erro matriz decisão: {str(e)}")
        return {
            "decisao": "HOLD",
            "tamanho_percent": 0,
            "prioridade": "baixa",
            "justificativa_matriz": f"Erro na matriz: {str(e)}"
        }

def _get_matriz_base_decisao(ciclo: str, setup: str) -> dict:
    """
    Matriz base Ciclo × Setup (da documentação V2)
    """
    
    # BOTTOM: Máxima agressividade em compras
    if ciclo == "BOTTOM":
        if setup == "OVERSOLD_EXTREMO":
            return {"decisao": "COMPRAR", "tamanho_percent": 50, "prioridade": "maxima"}
        elif setup in ["PULLBACK_TENDENCIA", "TESTE_SUPORTE"]:
            return {"decisao": "COMPRAR", "tamanho_percent": 40, "prioridade": "maxima"}
        elif setup == "ROMPIMENTO":
            return {"decisao": "COMPRAR", "tamanho_percent": 35, "prioridade": "alta"}
        else:
            return {"decisao": "COMPRAR", "tamanho_percent": 30, "prioridade": "alta"}
    
    # ACUMULAÇÃO: Compras agressivas
    elif ciclo == "ACUMULACAO":
        if setup == "OVERSOLD_EXTREMO":
            return {"decisao": "COMPRAR", "tamanho_percent": 40, "prioridade": "maxima"}
        elif setup == "PULLBACK_TENDENCIA":
            return {"decisao": "COMPRAR", "tamanho_percent": 35, "prioridade": "alta"}
        elif setup == "ROMPIMENTO":
            return {"decisao": "COMPRAR", "tamanho_percent": 25, "prioridade": "alta"}
        elif setup == "TESTE_SUPORTE":
            return {"decisao": "COMPRAR", "tamanho_percent": 30, "prioridade": "alta"}
        elif setup == "RESISTENCIA":
            return {"decisao": "HOLD", "tamanho_percent": 0, "prioridade": "baixa"}
        else:
            return {"decisao": "COMPRAR", "tamanho_percent": 20, "prioridade": "media"}
    
    # BULL INICIAL: Compras moderadas
    elif ciclo == "BULL_INICIAL":
        if setup == "OVERSOLD_EXTREMO":
            return {"decisao": "COMPRAR", "tamanho_percent": 30, "prioridade": "alta"}
        elif setup == "PULLBACK_TENDENCIA":
            return {"decisao": "COMPRAR", "tamanho_percent": 25, "prioridade": "media"}
        elif setup == "TESTE_SUPORTE":
            return {"decisao": "COMPRAR", "tamanho_percent": 20, "prioridade": "media"}
        elif setup == "ROMPIMENTO":
            return {"decisao": "COMPRAR", "tamanho_percent": 15, "prioridade": "media"}
        elif setup == "RESISTENCIA":
            return {"decisao": "REALIZAR", "tamanho_percent": 15, "prioridade": "baixa"}
        else:
            return {"decisao": "HOLD", "tamanho_percent": 0, "prioridade": "baixa"}
    
    # BULL MADURO: Hold + Realizações seletivas
    elif ciclo == "BULL_MADURO":
        if setup == "OVERSOLD_EXTREMO":
            return {"decisao": "COMPRAR", "tamanho_percent": 20, "prioridade": "media"}
        elif setup == "PULLBACK_TENDENCIA":
            return {"decisao": "COMPRAR", "tamanho_percent": 15, "prioridade": "baixa"}
        elif setup == "RESISTENCIA":
            return {"decisao": "REALIZAR", "tamanho_percent": 30, "prioridade": "alta"}
        elif setup == "ROMPIMENTO":
            return {"decisao": "REALIZAR", "tamanho_percent": 20, "prioridade": "media"}
        else:
            return {"decisao": "HOLD", "tamanho_percent": 0, "prioridade": "media"}
    
    # EUFORIA/TOPO: Ignorar compras, focar em vendas
    elif ciclo == "EUFORIA_TOPO":
        if setup in ["OVERSOLD_EXTREMO", "PULLBACK_TENDENCIA", "TESTE_SUPORTE", "ROMPIMENTO"]:
            return {"decisao": "IGNORAR", "tamanho_percent": 0, "prioridade": "nenhuma"}
        elif setup == "RESISTENCIA":
            return {"decisao": "REALIZAR", "tamanho_percent": 40, "prioridade": "maxima"}
        else:
            return {"decisao": "REALIZAR", "tamanho_percent": 30, "prioridade": "alta"}
    
    # Default para ciclos não mapeados
    else:
        return {"decisao": "HOLD", "tamanho_percent": 0, "prioridade": "baixa"}

def _aplicar_ajustes_contexto(decisao_base: dict, risco_data: dict, 
                             alavancagem_data: dict, mercado_data: dict) -> dict:
    """
    Aplica ajustes baseados no contexto atual (HF, alavancagem, etc)
    """
    decisao = decisao_base.copy()
    ajustes_aplicados = []
    
    # AJUSTE 1: Health Factor baixo reduz tamanho drasticamente
    hf = risco_data["health_factor"]
    if hf < 1.2:
        decisao["decisao"] = "REDUZIR_URGENTE"
        decisao["tamanho_percent"] = 70 if hf < 1.1 else 50
        ajustes_aplicados.append(f"HF {hf} < 1.2 força redução")
        
    elif hf < 1.5:
        # Reduzir tamanho das compras
        if decisao["decisao"] == "COMPRAR":
            decisao["tamanho_percent"] = int(decisao["tamanho_percent"] * 0.5)
            ajustes_aplicados.append(f"HF {hf} reduz compras 50%")
    
    # AJUSTE 2: Score de risco baixo
    score_risco = risco_data["score"]
    if score_risco < 40:
        if decisao["decisao"] == "COMPRAR":
            decisao["tamanho_percent"] = int(decisao["tamanho_percent"] * 0.6)
            ajustes_aplicados.append(f"Score risco {score_risco} reduz compras")
    
    # AJUSTE 3: Alavancagem no limite
    if not alavancagem_data["pode_aumentar"]:
        if decisao["decisao"] == "COMPRAR":
            decisao["decisao"] = "AJUSTAR_PRIMEIRO"
            decisao["tamanho_percent"] = 0
            ajustes_aplicados.append("Alavancagem no limite bloqueia compras")
    
    # AJUSTE 4: Capital livre insuficiente
    capital_percent = alavancagem_data["capital_livre_percent"]
    if capital_percent < 5:
        decisao["decisao"] = "BLOQUEADO"
        decisao["tamanho_percent"] = 0
        ajustes_aplicados.append(f"Capital {capital_percent}% < 5% bloqueia operações")
    
    # AJUSTE 5: Score mercado muito baixo
    score_mercado = mercado_data["score"]
    if score_mercado < 20:
        if decisao["decisao"] == "COMPRAR":
            decisao["tamanho_percent"] = int(decisao["tamanho_percent"] * 0.7)
            ajustes_aplicados.append(f"Score mercado {score_mercado} reduz agressividade")
    
    # Adicionar justificativa dos ajustes
    if ajustes_aplicados:
        decisao["justificativa_matriz"] = f"Base: {decisao_base['decisao']} {decisao_base['tamanho_percent']}%. Ajustes: {'; '.join(ajustes_aplicados)}"
    else:
        decisao["justificativa_matriz"] = f"Decisão matriz direta: {decisao['decisao']} {decisao['tamanho_percent']}%"
    
    return decisao

def _aplicar_filtros_emergencia(decisao: dict, health_factor: float, capital_percent: float) -> dict:
    """
    Filtros de emergência que sobrescrevem qualquer decisão
    """
    # Emergência crítica: HF muito baixo
    if health_factor < 1.1:
        return {
            "decisao": "EMERGENCIA_LIQUIDAR",
            "tamanho_percent": 80,
            "prioridade": "critica",
            "justificativa_matriz": f"EMERGÊNCIA: HF {health_factor} < 1.1 força liquidação imediata"
        }
    
    # Capital crítico
    if capital_percent < 2:
        return {
            "decisao": "BLOQUEADO_CAPITAL",
            "tamanho_percent": 0,
            "prioridade": "critica", 
            "justificativa_matriz": f"BLOQUEADO: Capital {capital_percent}% < 2% insuficiente"
        }
    
    return decisao

def _validar_decisao_final(decisao: dict) -> dict:
    """
    Validação final da decisão antes de retornar
    """
    # Garantir campos obrigatórios
    if "decisao" not in decisao:
        decisao["decisao"] = "HOLD"
    
    if "tamanho_percent" not in decisao:
        decisao["tamanho_percent"] = 0
        
    if "prioridade" not in decisao:
        decisao["prioridade"] = "baixa"
    
    # Garantir limites válidos
    decisao["tamanho_percent"] = max(0, min(100, decisao["tamanho_percent"]))
    
    return decisao