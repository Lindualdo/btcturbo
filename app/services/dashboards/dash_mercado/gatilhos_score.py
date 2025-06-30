# app/services/dashboards/dash_mercado/gatilhos_score.py

import logging

logger = logging.getLogger(__name__)

def aplicar_gatilhos_score(scores_data: dict) -> dict:
    """
    Aplica gatilhos de modificação de pesos baseado em condições de mercado
    
    Args:
        scores_data: Dados dos scores já calculados
        
    Returns:
        dict: scores_data com pesos modificados e score recalculado
    """
    try:
        logger.info("🎯 Aplicando gatilhos de score...")
        
        # Extrair dados necessários
        ciclo_data = scores_data.get("ciclo", {})
        tecnico_data = scores_data.get("tecnico", {})
        momentum_data = scores_data.get("momentum", {})
        
        # Valores dos indicadores
        mvrv = _extrair_valor_indicador(ciclo_data, "MVRV_Z")
        nupl = _extrair_valor_indicador(ciclo_data, "NUPL") 
        emas_alinhamento = _extrair_score_alinhamento_semanal(tecnico_data)
        
        # Pesos padrão
        pesos_originais = {"ciclo": 0.50, "momentum": 0.20, "tecnico": 0.30}
        novos_pesos = pesos_originais.copy()
        gatilho_ativado = None
        
        # APLICAR GATILHOS POR PRIORIDADE
        
        # 1. PRIORIDADE MÁXIMA: Zonas Extremas
        if mvrv is not None and nupl is not None:
            if mvrv > 2.8 or nupl > 0.65:
                novos_pesos = {"ciclo": 0.70, "tecnico": 0.20, "momentum": 0.10}
                gatilho_ativado = f"ZONA_TOPO (MVRV:{mvrv:.2f}, NUPL:{nupl:.2f})"
                
            elif mvrv < 1.0 or nupl < 0:
                novos_pesos = {"ciclo": 0.70, "tecnico": 0.20, "momentum": 0.10}
                gatilho_ativado = f"ZONA_FUNDO (MVRV:{mvrv:.2f}, NUPL:{nupl:.2f})"
        
        # 2. TENDÊNCIA CONFIRMADA: EMAs alinhadas
        if gatilho_ativado is None and emas_alinhamento == 100:
            novos_pesos = {"ciclo": 0.20, "tecnico": 0.70, "momentum": 0.10}
            gatilho_ativado = "TENDENCIA_CONFIRMADA (EMAs=100)"
        
        # 3. EVENTOS EXTREMOS (MOCKADO por enquanto)
        if gatilho_ativado is None:
            volume_extremo = _verificar_volume_extremo_mock()
            volatilidade_alta = _verificar_volatilidade_alta_mock()
            
            if volume_extremo:
                novos_pesos = {"momentum": 0.40, "ciclo": 0.40, "tecnico": 0.20}
                gatilho_ativado = "VOLUME_EXTREMO (mockado)"
                
            elif volatilidade_alta:
                novos_pesos = {"momentum": 0.40, "ciclo": 0.30, "tecnico": 0.30}
                gatilho_ativado = "VOLATILIDADE_ALTA (mockado)"
        
        # RECALCULAR SCORE COM NOVOS PESOS
        if gatilho_ativado:
            score_original = scores_data.get("score_consolidado", 0)
            score_ajustado = _recalcular_score_com_pesos(scores_data, novos_pesos)
            
            logger.info(f"✅ Gatilho ativado: {gatilho_ativado}")
            logger.info(f"📊 Pesos: Ciclo:{novos_pesos['ciclo']:.0%} Mom:{novos_pesos['momentum']:.0%} Téc:{novos_pesos['tecnico']:.0%}")
            logger.info(f"🎯 Score: {score_original:.1f} → {score_ajustado:.1f}")
            
            # Atualizar scores_data
            scores_data["score_consolidado"] = score_ajustado
            scores_data["classificacao_consolidada"] = _classificar_score(score_ajustado)
            
            # Dados para gravação no banco
            scores_data["pesos_utilizados"] = novos_pesos
            scores_data["gatilhos_acionados"] = gatilho_ativado
            scores_data["gatilho_aplicado"] = {
                "ativado": True,
                "tipo": gatilho_ativado,
                "pesos_originais": pesos_originais,
                "pesos_aplicados": novos_pesos,
                "score_original": score_original,
                "score_ajustado": score_ajustado
            }
        else:
            logger.info("ℹ️ Nenhum gatilho ativado - mantendo pesos padrão")
            
            # Dados padrão para gravação no banco
            scores_data["pesos_utilizados"] = pesos_originais
            scores_data["gatilhos_acionados"] = "NENHUM"
            scores_data["gatilho_aplicado"] = {"ativado": False}
        
        return scores_data
        
    except Exception as e:
        logger.error(f"❌ Erro aplicar gatilhos: {str(e)}")
        # Em caso de erro, retornar dados originais
        scores_data["gatilho_aplicado"] = {"ativado": False, "erro": str(e)}
        return scores_data

def _extrair_valor_indicador(bloco_data: dict, indicador_nome: str) -> float:
    """Extrai valor de indicador dos dados do bloco"""
    try:
        indicadores = bloco_data.get("indicadores", {})
        indicador = indicadores.get(indicador_nome, {})
        valor = indicador.get("valor")
        return float(valor) if valor is not None else None
    except (ValueError, TypeError):
        return None

def _extrair_score_alinhamento_semanal(tecnico_data: dict) -> int:
    """Extrai score de alinhamento semanal dos dados técnicos v3"""
    try:
        score_semanal = tecnico_data.get("score_semanal", {})
        score_alinhamento = score_semanal.get("score_alinhamento", 0)
        return int(float(score_alinhamento)) if score_alinhamento else 0
    except (ValueError, TypeError):
        return 0

def _verificar_volume_extremo_mock() -> bool:
    """MOCKADO: Verifica se volume > 3x média 24h"""
    # TODO: Implementar verificação real via TradingView
    return False  # Sempre False por enquanto

def _verificar_volatilidade_alta_mock() -> bool:
    """MOCKADO: Verifica se volatilidade > 5% dia"""
    # TODO: Implementar cálculo real de volatilidade
    return False  # Sempre False por enquanto

def _recalcular_score_com_pesos(scores_data: dict, novos_pesos: dict) -> float:
    """Recalcula score consolidado com novos pesos"""
    try:
        score_ciclo = float(scores_data["ciclo"]["score_consolidado"])
        score_momentum = float(scores_data["momentum"]["score_consolidado"])
        score_tecnico = float(scores_data["tecnico"]["score_consolidado"])
        
        score_recalculado = (
            (score_ciclo * novos_pesos["ciclo"]) +
            (score_momentum * novos_pesos["momentum"]) +
            (score_tecnico * novos_pesos["tecnico"])
        )
        
        return round(score_recalculado, 1)
        
    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"❌ Erro recalcular score: {str(e)}")
        return scores_data.get("score_consolidado", 0)

def _classificar_score(score: float) -> str:
    """Classifica score consolidado"""
    if score >= 80.0:
        return "ótimo"
    elif score >= 60.0:
        return "bom"
    elif score >= 40.0:
        return "neutro"
    elif score >= 20.0:
        return "ruim"
    else:
        return "crítico"