# app/services/analises/analise_tatica_completa.py - CORRIGIDO (BBW REAL)

from datetime import datetime
import logging
from app.services.utils.helpers.analise.matriz_cenarios_completos_helper import (
    avaliar_cenario_completo, calcular_score_cenario_completo,
    gerar_insights_cenario, gerar_alertas_cenario
)
from app.services.utils.helpers.analise.matriz_tatica_helper import encontrar_acao_tatica, calcular_score_tatico
from app.services.utils.helpers.rsi_helper import obter_rsi_diario
from app.services.utils.helpers.analise.ema144_live_helper import obter_ema144_distance_atualizada
from app.services.utils.helpers.analise.simulacao_helper import obter_dados_posicao, simular_impacto_posicao
from app.services.utils.helpers.bbw_calculator import obter_bbw_com_score  # ← ADICIONADO

# Importar services das outras camadas
from app.services.analises.analise_mercado import calcular_analise_mercado
from app.services.analises.analise_risco import calcular_analise_risco
from app.services.analises.analise_alavancagem import calcular_analise_alavancagem



def calcular_analise_tatica_completa():
    """
    FUNÇÃO PRINCIPAL: Análise Tática Completa com 8 Cenários
    
    Integra todas as 4 camadas:
    1. Análise de Mercado
    2. Análise de Risco  
    3. Análise de Alavancagem
    4. Matriz Completa de Cenários
    """
    try:
        logging.info("🎯 Iniciando análise tática COMPLETA (8 cenários)...")
        
        # ==========================================
        # 1. COLETA DE DADOS DAS 4 CAMADAS
        # ==========================================
        
        # 1.1 Dados táticos básicos (EMA + RSI)
        try:
            ema_distance = obter_ema144_distance_atualizada()
            rsi_diario = obter_rsi_diario()
            logging.info(f"✅ Dados táticos: EMA={ema_distance:+.1f}%, RSI={rsi_diario:.1f}")
        except Exception as e:
            return _erro_dados_criticos("tacticos", str(e))
        
        # 1.2 Análise de Mercado (Camada 1)
        try:
            dados_mercado = calcular_analise_mercado()
            if dados_mercado.get("status") != "success":
                raise Exception(dados_mercado.get("erro", "Análise mercado falhou"))
            score_mercado = dados_mercado["score_consolidado"]
            logging.info(f"✅ Score Mercado: {score_mercado}")
        except Exception as e:
            return _erro_dados_criticos("mercado", str(e))
        
        # 1.3 Análise de Risco (Camada 2)
        try:
            dados_risco = calcular_analise_risco()
            if dados_risco.get("status") != "success":
                raise Exception(dados_risco.get("erro", "Análise risco falhou"))
            score_risco = dados_risco["score_consolidado"]
            logging.info(f"✅ Score Risco: {score_risco}")
        except Exception as e:
            return _erro_dados_criticos("risco", str(e))
        
        # 1.4 Análise de Alavancagem (Camada 3)
        try:
            dados_alavancagem = calcular_analise_alavancagem()
            if dados_alavancagem.get("status") != "success":
                raise Exception(dados_alavancagem.get("erro", "Análise alavancagem falhou"))
            
            # Extrair MVRV dos dados de alavancagem
            mvrv = dados_alavancagem["inputs"]["mvrv_z_score"]
            max_leverage_permitida = dados_alavancagem["parametros"]["max_leverage"]
            logging.info(f"✅ MVRV: {mvrv}, Max Leverage: {max_leverage_permitida}x")
        except Exception as e:
            return _erro_dados_criticos("alavancagem", str(e))
        
        # 1.5 Dados extras (obrigatórios para cenários específicos)
        dados_extras = {}
        try:
            posicao_atual = obter_dados_posicao()
            if posicao_atual and dados_risco.get("composicao", {}).get("breakdown"):
                breakdown_risco = dados_risco["composicao"]["breakdown"]
                
                # Health Factor - FAIL FAST se não disponível
                hf_valor = breakdown_risco.get("health_factor", {}).get("valor_display")
                if not hf_valor or hf_valor == "N/A":
                    return _erro_dados_criticos("health_factor", "Health Factor indisponível - verificar coleta dados AAVE")
                
                try:
                    dados_extras["health_factor"] = float(str(hf_valor).replace("$", "").replace(",", ""))
                except (ValueError, TypeError):
                    return _erro_dados_criticos("health_factor", f"Health Factor inválido: {hf_valor}")
                
                # Distância Liquidação - FAIL FAST se não disponível  
                dist_valor = breakdown_risco.get("dist_liquidacao", {}).get("valor_display")
                if not dist_valor or dist_valor == "N/A":
                    return _erro_dados_criticos("dist_liquidacao", "Distância liquidação indisponível - verificar cálculo risco")
                
                try:
                    dados_extras["dist_liquidacao"] = float(str(dist_valor).replace("%", ""))
                except (ValueError, TypeError):
                    return _erro_dados_criticos("dist_liquidacao", f"Distância liquidação inválida: {dist_valor}")
                
                logging.info(f"✅ Dados extras: HF={dados_extras['health_factor']}, Dist={dados_extras['dist_liquidacao']}%")
            else:
                return _erro_dados_criticos("posicao_risco", "Dados de posição ou breakdown risco indisponíveis")
            
            # BBW - OBRIGATÓRIO para cenários específicos (SEM FALLBACK)
            try:
                bbw_data = obter_bbw_com_score()
                
                if not bbw_data or "bbw_percentage" not in bbw_data:
                    return _erro_dados_criticos("bbw", "BBW retornou dados inválidos")
                
                dados_extras["bbw_percentage"] = bbw_data["bbw_percentage"]
                
                # Log detalhado do BBW
                estado = bbw_data.get("estado", "unknown")
                score_bbw = bbw_data.get("score_bbw", 0)
                logging.info(f"✅ BBW obtido: {dados_extras['bbw_percentage']:.2f}% ({estado}, score: {score_bbw})")
                
            except ImportError as e:
                return _erro_dados_criticos("bbw", f"BBW Calculator não encontrado: {str(e)} - verificar implementação")
            except Exception as e:
                return _erro_dados_criticos("bbw", f"Erro obtendo BBW: {str(e)} - verificar conexão TradingView")
            
        except Exception as e:
            return _erro_dados_criticos("dados_extras", f"Falha crítica na coleta: {str(e)}")
        
        # ==========================================
        # 2. MATRIZ TÁTICA BÁSICA (EMA + RSI)
        # ==========================================
        
        regra_tatica_basica = encontrar_acao_tatica(ema_distance, rsi_diario)
        score_tatico_basico = calcular_score_tatico(
            regra_tatica_basica["acao"], 
            regra_tatica_basica["tamanho"], 
            ema_distance, 
            rsi_diario
        )
        
        # ==========================================
        # 3. AVALIAÇÃO DE CENÁRIOS COMPLETOS
        # ==========================================
        
        cenario_identificado, motivo_cenario = avaliar_cenario_completo(
            score_mercado=score_mercado,
            score_risco=score_risco,
            mvrv=mvrv,
            ema_distance=ema_distance,
            rsi_diario=rsi_diario,
            dados_extras=dados_extras
        )
        
        # ==========================================
        # 4. DECISÃO FINAL INTEGRADA
        # ==========================================
        
        # Se nenhum cenário específico foi identificado, usar matriz tática básica
        if cenario_identificado is None:
            logging.info("📊 Usando matriz tática básica como fallback")
            
            # Score final = score tático básico + pequeno bonus das outras camadas
            score_final = score_tatico_basico + (score_mercado * 0.2) + (score_risco * 0.2)
            score_final = max(0, min(100, score_final))
            
            # Decisão = matriz tática básica
            acao_final = regra_tatica_basica["acao"]
            tamanho_final = regra_tatica_basica["tamanho"]
            decisao_final = "MATRIZ_TATICA_BASICA"
            
            # Criar cenário fictício para uniformizar resposta
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
            logging.info(f"🎯 Cenário específico: {cenario_identificado['nome']}")
            
            # Score final integrado
            score_final = calcular_score_cenario_completo(
                cenario_identificado,
                score_tatico_basico,
                score_mercado,
                score_risco
            )
            
            # Decisão final (cenário override matriz básica)
            acao_final_dict = cenario_identificado["acao"]
            decisao_final = acao_final_dict["decisao"]
            
            cenario_display = cenario_identificado
            override_cenario = True
        
        # Mapeamento de decisões para ações padrão
        if decisao_final in ["ENTRAR", "ADICIONAR_AGRESSIVO"]:
            acao_padrao = "ADICIONAR"
            tamanho_final = acao_final_dict.get("tamanho_percent", 40)
        elif decisao_final in ["REALIZAR_PARCIAL", "REALIZAR_AGRESSIVO"]:
            acao_padrao = "REALIZAR"
            tamanho_final = acao_final_dict.get("tamanho_percent", 30)
        elif decisao_final in ["REDUZIR_DEFENSIVO", "EMERGENCIA_REDUZIR"]:
            acao_padrao = "REALIZAR"
            tamanho_final = acao_final_dict.get("tamanho_percent", 70)
        elif decisao_final == "MATRIZ_TATICA_BASICA":
            acao_padrao = regra_tatica_basica["acao"]
            tamanho_final = regra_tatica_basica["tamanho"]
        else:
            acao_padrao = "HOLD"
            tamanho_final = 0
        
        # ==========================================
        # 5. SIMULAÇÃO E INSIGHTS
        # ==========================================
        
        # Simulação de impacto
        simulacao = None
        if posicao_atual:
            try:
                simulacao = simular_impacto_posicao(acao_padrao, tamanho_final, posicao_atual)
                if "erro" in simulacao:
                    simulacao = None
            except Exception as e:
                logging.warning(f"⚠️ Erro simulação: {str(e)}")
        
        # Contexto para insights/alertas
        dados_contexto = {
            "mvrv": mvrv,
            "score_mercado": score_mercado,
            "score_risco": score_risco,
            "ema_distance": ema_distance,
            "rsi_diario": rsi_diario,
            "max_leverage": max_leverage_permitida
        }
        
        # Insights e alertas (cenário específico ou matriz básica)
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
        
        # ==========================================
        # 6. RESPOSTA CONSOLIDADA
        # ==========================================
        
        return {
            "analise": "tatica_completa",
            "versao": "8_cenarios_integrados",
            "timestamp": datetime.utcnow().isoformat(),
            "score_consolidado": round(score_final, 1),
            "score_maximo": 100,
            "classificacao": _classificar_score_final(score_final),
            "acao_recomendada": _formatar_acao_final(acao_final_dict),
            
            # Cenário identificado
            "cenario_identificado": {
                "id": cenario_display["id"],
                "nome": cenario_display["nome"],
                "descricao": cenario_display["descricao"],
                "prioridade": cenario_display["prioridade"],
                "motivo_escolha": motivo_cenario,
                "override_tatico": override_cenario,
                "tipo": "cenario_especifico" if override_cenario else "matriz_tatica_basica"
            },
            
            # Decisão final integrada
            "decisao_final": {
                "acao": acao_padrao,
                "tamanho_percent": tamanho_final,
                "decisao_cenario": decisao_final,
                "alavancagem_recomendada": acao_final_dict["alavancagem_recomendada"],
                "stop_loss_percent": acao_final_dict["stop_loss"],
                "target": acao_final_dict["target"],
                "justificativa": acao_final_dict["justificativa"]
            },
            
            # Inputs das 4 camadas
            "dados_camadas": {
                "mercado": {
                    "score": score_mercado,
                    "classificacao": dados_mercado["classificacao"],
                    "favoravel": dados_mercado["mercado_favoravel"]
                },
                "risco": {
                    "score": score_risco,
                    "classificacao": dados_risco["classificacao"],
                    "seguro": dados_risco["posicao_segura"]
                },
                "alavancagem": {
                    "max_leverage": max_leverage_permitida,
                    "fase_mercado": dados_alavancagem["parametros"]["fase_mercado"],
                    "classificacao": dados_alavancagem["classificacao"]
                },
                "tatico_basico": {
                    "ema_distance": round(ema_distance, 1),
                    "rsi_diario": round(rsi_diario, 0),
                    "acao_matriz": regra_tatica_basica["acao"],
                    "tamanho_matriz": regra_tatica_basica["tamanho"],
                    "score_basico": round(score_tatico_basico, 1)
                }
            },
            
            # Composição do score final
            "composicao_score": {
                "formula": "Score = (Tático×40%) + (Mercado×30%) + (Risco×30%) + Bonus_Cenário" if override_cenario else "Score = Tático + (Mercado×20%) + (Risco×20%)",
                "calculo": f"Score = ({score_tatico_basico:.1f}×0.4) + ({score_mercado:.1f}×0.3) + ({score_risco:.1f}×0.3) + {cenario_display.get('score_bonus', 0)}" if override_cenario else f"Score = {score_tatico_basico:.1f} + ({score_mercado:.1f}×0.2) + ({score_risco:.1f}×0.2)",
                "score_base": round((score_tatico_basico * 0.4) + (score_mercado * 0.3) + (score_risco * 0.3), 1) if override_cenario else round(score_tatico_basico + (score_mercado * 0.2) + (score_risco * 0.2), 1),
                "bonus_cenario": cenario_display.get("score_bonus", 0),
                "score_final": round(score_final, 1),
                "metodo": "cenario_especifico" if override_cenario else "matriz_tatica_basica"
            },
            
            # Análise contextual
            "analise_contextual": {
                "insights": insights_finais,
                "confianca_decisao": _avaliar_confianca_integrada(score_final, cenario_display) if override_cenario else _avaliar_confianca_matriz_basica(score_final),
                "timing_execucao": _avaliar_timing_integrado(cenario_display) if override_cenario else _avaliar_timing_matriz_basica(score_final),
                "nivel_urgencia": _avaliar_urgencia(cenario_display) if override_cenario else "BAIXA",
                "override_ativo": override_cenario
            },
            
            # Comparação matriz básica vs cenário
            "comparacao_decisoes": {
                "matriz_basica": {
                    "acao": regra_tatica_basica["acao"],
                    "tamanho": regra_tatica_basica["tamanho"],
                    "justificativa": regra_tatica_basica["justificativa"]
                },
                "decisao_final": {
                    "acao": acao_padrao,
                    "tamanho": tamanho_final,
                    "justificativa": acao_final_dict["justificativa"]
                },
                "decisao_prevaleceu": "cenario_especifico" if override_cenario else "matriz_basica",
                "motivo_escolha": f"Cenário '{cenario_display['nome']}' tem prioridade {cenario_display['prioridade']}" if override_cenario else "Nenhum cenário específico atendido"
            },
            
            # Alertas integrados
            "alertas": alertas_finais,
            
            # Simulação (se disponível)
            "simulacao": simulacao or {
                "status": "indisponivel",
                "motivo": "Dados de posição não encontrados"
            },
            
            "status": "success"
        }
        
    except Exception as e:
        logging.error(f"❌ Erro na análise tática completa: {str(e)}")
        return {
            "analise": "tatica_completa",
            "timestamp": datetime.utcnow().isoformat(),
            "score_consolidado": 0,
            "classificacao": "erro",
            "acao_recomendada": "Sistema com falha crítica - não operar",
            "status": "error",
            "erro": str(e)
        }

# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================

def _erro_dados_criticos(componente: str, erro: str) -> dict:
    """Retorna erro padronizado para dados críticos indisponíveis"""
    return {
        "analise": "tatica_completa",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "error",
        "erro": f"Dados críticos indisponíveis: {componente}",
        "detalhes": erro,
        "componente_faltante": componente,
        "acao_recomendada": f"Corrigir {componente} antes de tomar decisões táticas"
    }

def _classificar_score_final(score: float) -> str:
    """Classifica score final integrado"""
    if score >= 85:
        return "oportunidade_excepcional"
    elif score >= 70:
        return "oportunidade_excelente"
    elif score >= 55:
        return "oportunidade_boa"
    elif score >= 40:
        return "oportunidade_neutra"
    elif score >= 25:
        return "condições_desfavoráveis"
    else:
        return "evitar_operações"

def _formatar_acao_final(acao_final: dict) -> str:
    """Formata ação recomendada final"""
    decisao = acao_final["decisao"]
    alavancagem = acao_final["alavancagem_recomendada"]
    
    if decisao == "ENTRAR":
        return f"Entrar com {alavancagem}x - {acao_final['justificativa']}"
    elif "ADICIONAR" in decisao:
        tamanho = acao_final.get("tamanho_percent", 35)
        return f"Adicionar {tamanho}% à posição - {acao_final['justificativa']}"
    elif "REALIZAR" in decisao:
        tamanho = acao_final.get("tamanho_percent", 30)
        return f"Realizar {tamanho}% da posição - {acao_final['justificativa']}"
    elif "REDUZIR" in decisao:
        tamanho = acao_final.get("tamanho_percent", 50)
        return f"Reduzir {tamanho}% da posição - {acao_final['justificativa']}"
    elif "EMERGENCIA" in decisao:
        tamanho = acao_final.get("tamanho_percent", 80)
        return f"EMERGÊNCIA: Reduzir {tamanho}% IMEDIATAMENTE - {acao_final['justificativa']}"
    else:
        return f"Manter posição atual - {acao_final['justificativa']}"

def _avaliar_confianca_integrada(score: float, cenario: dict) -> str:
    """Avalia confiança considerando score e prioridade do cenário"""
    prioridade = cenario["prioridade"]
    
    if cenario.get("override"):
        return "maxima"  # Override sempre tem confiança máxima
    elif prioridade <= 1 and score >= 70:
        return "alta"
    elif prioridade <= 2 and score >= 60:
        return "alta"
    elif score >= 50:
        return "media"
    else:
        return "baixa"

def _avaliar_timing_integrado(cenario: dict) -> str:
    """Avalia timing de execução baseado no cenário"""
    if cenario.get("override"):
        return "imediato_emergencia"
    elif cenario["prioridade"] == 0:
        return "imediato_critico"
    elif cenario["prioridade"] == 1:
        return "24_horas"
    elif cenario["prioridade"] == 2:
        return "48_horas"
    else:
        return "monitorar_evolucao"

def _avaliar_urgencia(cenario: dict) -> str:
    """Avalia nível de urgência"""
    if cenario.get("override"):
        return "CRÍTICA"
    elif cenario["prioridade"] <= 1:
        return "ALTA"
    elif cenario["prioridade"] == 2:
        return "MÉDIA"
    else:
        return "BAIXA"

def _avaliar_confianca_matriz_basica(score: float) -> str:
    """Avalia confiança da matriz tática básica"""
    if score >= 70:
        return "alta"
    elif score >= 50:
        return "media"
    else:
        return "baixa"

def _avaliar_timing_matriz_basica(score: float) -> str:
    """Avalia timing da matriz tática básica"""
    if score >= 80:
        return "24_horas"
    elif score >= 60:
        return "48_horas"
    else:
        return "monitorar_evolucao"