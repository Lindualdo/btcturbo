# app/services/analises/tatica/logica_cenarios.py

import logging
from app.services.utils.helpers.analise.matriz_cenarios_completos_helper import (
    avaliar_cenario_completo, gerar_insights_cenario, gerar_alertas_cenario
)
from app.services.utils.helpers.analise.matriz_tatica_helper import encontrar_acao_tatica, calcular_score_tatico

logger = logging.getLogger(__name__)

def processar_decisao_tatica(dados_coletados):
    """
    Processa decisão tática usando cenários específicos ou matriz básica
    
    Args:
        dados_coletados: Dados de todas as camadas
        
    Returns:
        dict: Decisão final estruturada
    """
    try:
        # Extrair dados necessários
        ema_distance = dados_coletados["ema_distance"]
        rsi_diario = dados_coletados["rsi_diario"]
        score_mercado = dados_coletados["score_mercado"]
        score_risco = dados_coletados["score_risco"]
        mvrv = dados_coletados["mvrv"]
        max_leverage_permitida = dados_coletados["max_leverage_permitida"]
        dados_extras = dados_coletados["dados_extras"]
        
        # 1. Matriz tática básica (sempre calcular)
        regra_tatica_basica = encontrar_acao_tatica(ema_distance, rsi_diario)
        score_tatico_basico = calcular_score_tatico(
            regra_tatica_basica["acao"], 
            regra_tatica_basica["tamanho"], 
            ema_distance, 
            rsi_diario
        )
        
        logger.info(f"📊 Matriz básica: {regra_tatica_basica['acao']} {regra_tatica_basica['tamanho']}%")
        
        # 2. Avaliação de cenários completos
        cenario_identificado, motivo_cenario = avaliar_cenario_completo(
            score_mercado=score_mercado,
            score_risco=score_risco,
            mvrv=mvrv,
            ema_distance=ema_distance,
            rsi_diario=rsi_diario,
            dados_extras=dados_extras
        )
        
        # 3. Decisão final integrada
        if cenario_identificado is None or cenario_identificado["id"] == "indefinido":
            logger.info("📊 Usando matriz tática básica")
            
            # Usar matriz básica
            acao_final = regra_tatica_basica["acao"]
            tamanho_final = regra_tatica_basica["tamanho"]
            decisao_final = "MATRIZ_TATICA_BASICA"
            
            # Cenário fictício para uniformizar resposta
            cenario_display = {
                "id": "matriz_tatica_basica",
                "nome": "Matriz Tática Básica",
                "descricao": "Decisão baseada apenas em EMA144 + RSI Diário",
                "prioridade": 98,
                "score_bonus": 0
            }
            
            acao_final_dict = {
                "decisao": decisao_final,
                "tamanho_percent": tamanho_final,
                "alavancagem_recomendada": max_leverage_permitida,
                "stop_loss": 10,
                "target": "Baseado em EMA144 + RSI",
                "justificativa": regra_tatica_basica["justificativa"]
            }
            
            override_cenario = False
            
        else:
            # Cenário específico identificado
            logger.info(f"🎯 Cenário específico: {cenario_identificado['nome']}")
            
            acao_final_dict = cenario_identificado["acao"]
            decisao_final = acao_final_dict["decisao"]
            cenario_display = cenario_identificado
            override_cenario = True
        
        # 4. Mapear decisões para ações padrão
        if decisao_final in ["ENTRAR", "ADICIONAR_AGRESSIVO"]:
            acao_padrao = "ADICIONAR"
            tamanho_final = acao_final_dict.get("tamanho_percent", 40)
        elif decisao_final in ["REALIZAR_PARCIAL", "REALIZAR_AGRESSIVO"]:
            acao_padrao = "REALIZAR"
            tamanho_final = acao_final_dict.get("tamanho_percent", 30)
        elif decisao_final in ["REDUZIR_DEFENSIVO", "EMERGENCIA_REDUZIR"]:
            acao_padrao = "REALIZAR"
            tamanho_final = acao_final_dict.get("tamanho_percent", 70)
        elif decisao_final == "ACUMULAR_SPOT_APENAS":  # Bear profundo corrigido
            acao_padrao = "ADICIONAR"
            tamanho_final = acao_final_dict.get("tamanho_percent", 75)
        elif decisao_final == "MATRIZ_TATICA_BASICA":
            acao_padrao = regra_tatica_basica["acao"]
            tamanho_final = regra_tatica_basica["tamanho"]
        else:
            acao_padrao = "HOLD"
            tamanho_final = 0
        
        # 5. Gerar insights e alertas
        dados_contexto = {
            "mvrv": mvrv,
            "score_mercado": score_mercado,
            "score_risco": score_risco,
            "ema_distance": ema_distance,
            "rsi_diario": rsi_diario,
            "max_leverage": max_leverage_permitida
        }
        
        if override_cenario:
            insights_finais = gerar_insights_cenario(cenario_display, dados_contexto)
            alertas_finais = gerar_alertas_cenario(cenario_display, dados_contexto)
        else:
            # Insights da matriz tática básica
            insights_finais = [
                "📊 Decisão baseada em matriz tática básica (EMA144 + RSI)",
                f"🎯 Condições não mapeadas nos 8 cenários específicos"
            ]
            
            if acao_padrao == "ADICIONAR":
                insights_finais.append("💎 Oportunidade de acumulação identificada")
            elif acao_padrao == "REALIZAR":
                insights_finais.append("💰 Momento de proteção de lucros")
            else:
                insights_finais.append("⏳ Aguardar melhores condições")
            
            alertas_finais = [
                f"📊 EMA144: {ema_distance:+.1f}% | RSI: {rsi_diario:.0f}",
                f"🎯 Matriz básica: {acao_padrao} {tamanho_final}%" if tamanho_final > 0 else "🎯 Manter posição atual",
                "📈 Usar alavancagem permitida baseada em MVRV"
            ]
        
        return {
            "cenario_identificado": cenario_display,
            "motivo_cenario": motivo_cenario,
            "override_cenario": override_cenario,
            "acao_final_dict": acao_final_dict,
            "acao_padrao": acao_padrao,
            "tamanho_final": tamanho_final,
            "decisao_final": decisao_final,
            "regra_tatica_basica": regra_tatica_basica,
            "insights_finais": insights_finais,
            "alertas_finais": alertas_finais,
            "dados_contexto": dados_contexto
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na lógica de cenários: {str(e)}")
        raise