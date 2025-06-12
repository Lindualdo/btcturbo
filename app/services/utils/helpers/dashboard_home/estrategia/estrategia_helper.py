# app/services/utils/helpers/dashboard_home/estrategia_helper.py

import logging
from app.services.utils.helpers.analise.matriz_cenarios_completos_helper import avaliar_cenario_completo
from app.services.utils.helpers.analise.matriz_tatica_helper import encontrar_acao_tatica
from app.services.utils.helpers.analise.ema144_live_helper import obter_ema144_distance_atualizada
from app.services.utils.helpers.rsi_helper import obter_rsi_diario
from .filtros_protecao_helper import aplicar_filtros_protecao
from .estrategia_formatacao_helper import obter_dados_btc_validados, mapear_decisao_cenario, determinar_urgencia
from .estrategia_response_helper import criar_resposta_estrategia
from .fase_mercado_helper import identificar_fase_mercado

logger = logging.getLogger(__name__)




def get_estrategia_data(dados_dashboard: dict = None) -> dict:
    """
    Coleta dados da estratégia: ação, cenário, justificativa baseado nas matrizes
    
    Args:
        dados_dashboard: Dados dos outros módulos (mercado, risco, alavancagem)
    
    Returns:
        dict com campos da estratégia ou erro
    """
    try:
        logger.info("🎯 Coletando dados da estratégia...")
        
        # 1. Obter dados técnicos necessários com VALIDAÇÃO RIGOROSA
        ema_distance = obter_ema144_distance_atualizada()
        rsi_diario = obter_rsi_diario()
        ema_valor, btc_price, data_timestamp = obter_dados_btc_validados()
        
        # 2. Extrair dados dos outros módulos do dashboard
        if not dados_dashboard:
            raise Exception("Dados do dashboard são obrigatórios")
        
        mercado_data = dados_dashboard.get("mercado", {})
        risco_data = dados_dashboard.get("risco", {})
        
        score_mercado = float(mercado_data.get("campos", {}).get("score_mercado", 0))
        score_risco = float(risco_data.get("campos", {}).get("score_risco", 0))
        mvrv_valor = float(mercado_data.get("campos", {}).get("mvrv_valor", 0))
        health_factor = float(risco_data.get("campos", {}).get("health_factor", 0))
        dist_liquidacao = float(risco_data.get("campos", {}).get("dist_liquidacao", 0))
        
        # ====================================================================
        # CAMADA 1: FILTROS DE PROTEÇÃO - RETORNA IMEDIATAMENTE SE ACIONADO
        # ====================================================================
        
        acao_protecao = aplicar_filtros_protecao(
            dados_dashboard, mvrv_valor, ema_distance, rsi_diario, 
            btc_price, ema_valor, data_timestamp
        )
        
        if acao_protecao:
            return acao_protecao
        
        # ====================================================================
        # A PARTIR DAQUI: CÓDIGO ORIGINAL MANTIDO 100% INTACTO
        # ====================================================================
        
        # Identificar fase do mercado
        fase_mercado = identificar_fase_mercado(mvrv_valor)

        # VALIDAÇÃO: Calcular distância manualmente para conferir
        calculated_distance = ((btc_price - ema_valor) / ema_valor) * 100
        distance_diff = abs(ema_distance - calculated_distance)
        
        logger.info(f"📊 VALIDAÇÃO DADOS:")
        logger.info(f"💰 BTC Price: ${btc_price:,.2f} (timestamp: {data_timestamp})")
        logger.info(f"📈 EMA144: ${ema_valor:,.2f}")
        logger.info(f"📏 Distance API: {ema_distance:+.2f}%")
        logger.info(f"🔢 Distance Calc: {calculated_distance:+.2f}%")
        logger.info(f"⚠️ Diferença: {distance_diff:.2f}%")
        logger.info(f"📊 RSI: {rsi_diario:.1f}, Mercado: {score_mercado:.1f}, Risco: {score_risco:.1f}")
        
        # ALERTA se diferença > 0.5%
        if distance_diff > 0.5:
            logger.warning(f"🚨 DIVERGÊNCIA NOS DADOS! Diferença: {distance_diff:.2f}%")
            logger.warning(f"🚨 Usando distância calculada: {calculated_distance:+.2f}%")
            ema_distance = round(calculated_distance, 2)  # Usar cálculo manual
        
        # 3. Avaliar cenários completos primeiro
        cenario, motivo_escolha = avaliar_cenario_completo(
            score_mercado=score_mercado,
            score_risco=score_risco,
            mvrv=mvrv_valor,
            ema_distance=ema_distance,
            rsi_diario=rsi_diario,
            dados_extras={
                "health_factor": health_factor,
                "dist_liquidacao": dist_liquidacao,
                "bbw_percentage": 15.0  # Valor padrão
            }
        )
        
        # 4. Processar resultado do cenário
        if cenario["id"] != "indefinido":
            # Cenário específico encontrado
            acao = mapear_decisao_cenario(cenario["acao"]["decisao"])
            tamanho_percent = cenario["acao"].get("tamanho_percent", 0)
            justificativa = cenario["acao"]["justificativa"]
            urgencia = determinar_urgencia(cenario)
            matriz_usada = "cenarios_completos"
            cenario_nome = fase_mercado
            
        else:
            # Fallback: usar matriz básica EMA144 + RSI
            logger.info("📋 Usando matriz básica EMA144 + RSI (fallback)")
            regra_tatica = encontrar_acao_tatica(ema_distance, rsi_diario)
            
            acao = regra_tatica["acao"]
            tamanho_percent = regra_tatica["tamanho"]
            justificativa = regra_tatica["justificativa"]
            urgencia = "baixa"
            matriz_usada = "matriz_basica"
            cenario_nome = fase_mercado
        
        # 5. Determinar urgência se não definida
        if cenario.get("override"):
            urgencia = "critica"
        elif cenario["prioridade"] <= 1:
            urgencia = "alta"
        elif cenario["prioridade"] <= 2:
            urgencia = "media"
        else:
            urgencia = "baixa"
        
        # 6. Campos para PostgreSQL + JSON unificado
        dados_tecnicos = {
            "ema_distance": ema_distance,
            "ema_valor": ema_valor,
            "rsi_diario": rsi_diario,
            "btc_price": btc_price,
            "score_mercado": score_mercado,
            "score_risco": score_risco,
            "mvrv_valor": mvrv_valor,
            "data_timestamp": data_timestamp,
            "calculated_distance": round(calculated_distance, 2)
        }
        
        logger.info(f"✅ Estratégia: {acao} {tamanho_percent}% - {cenario_nome} ({urgencia})")
        
        return criar_resposta_estrategia(
            acao=acao,
            tamanho_percent=tamanho_percent,
            cenario=cenario_nome,
            justificativa=justificativa,
            urgencia=urgencia,
            matriz_usada=matriz_usada,
            dados_tecnicos=dados_tecnicos,
            fonte=f"{matriz_usada} + ema144_live + rsi_helper"
        )
        
    except Exception as e:
        logger.error(f"❌ Erro na estratégia: {str(e)}")
        return {
            "status": "error",
            "erro": str(e),
            "campos": {
                "acao_estrategia": "ERROR",
                "tamanho_percent_estrategia": 0,
                "cenario_estrategia": "erro",
                "justificativa_estrategia": "Sistema indisponível",
                "urgencia_estrategia": "baixa",
                "ema_distance": 0.0,
                "ema_valor": 0.0,
                "rsi_diario": 0.0,
                "matriz_usada": "erro"
            }
        }