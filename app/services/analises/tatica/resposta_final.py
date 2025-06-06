# app/services/analises/tatica/resposta_final.py

from datetime import datetime
import logging
from app.services.utils.helpers.analise.simulacao_helper import simular_impacto_posicao

logger = logging.getLogger(__name__)

def montar_resposta_final(dados_coletados, decisao_processada):
    """
    Monta resposta final da análise tática completa
    
    Args:
        dados_coletados: Dados de todas as camadas
        decisao_processada: Decisão táctica processada
        
    Returns:
        dict: Resposta completa da API
    """
    try:
        # Extrair dados
        posicao_atual = dados_coletados["posicao_atual"]
        dados_mercado = dados_coletados["dados_mercado"]
        dados_risco = dados_coletados["dados_risco"]
        dados_alavancagem = dados_coletados["dados_alavancagem"]
        
        # Extrair decisão
        cenario_display = decisao_processada["cenario_identificado"]
        acao_final_dict = decisao_processada["acao_final_dict"]
        acao_padrao = decisao_processada["acao_padrao"]
        tamanho_final = decisao_processada["tamanho_final"]
        regra_tatica_basica = decisao_processada["regra_tatica_basica"]
        override_cenario = decisao_processada["override_cenario"]
        
        # Simulação de impacto
        simulacao = None
        if posicao_atual:
            try:
                simulacao = simular_impacto_posicao(acao_padrao, tamanho_final, posicao_atual)
                if "erro" in simulacao:
                    simulacao = None
            except Exception as e:
                logger.warning(f"⚠️ Erro simulação: {str(e)}")
        
        # Montar resposta final (conforme documentação - SEM score consolidado)
        return {
            "analise": "tatica_completa",
            "versao": "4_camadas_independentes", 
            "timestamp": datetime.utcnow().isoformat(),
            "acao_recomendada": _formatar_acao_final(acao_final_dict),
            
            # Cenário identificado
            "cenario_identificado": {
                "id": cenario_display["id"],
                "nome": cenario_display["nome"],
                "descricao": cenario_display["descricao"],
                "prioridade": cenario_display["prioridade"],
                "motivo_escolha": decisao_processada["motivo_cenario"],
                "override_tatico": override_cenario,
                "tipo": "cenario_especifico" if override_cenario else "matriz_tatica_basica"
            },
            
            # Decisão final integrada
            "decisao_final": {
                "acao": acao_padrao,
                "tamanho_percent": tamanho_final,
                "decisao_cenario": decisao_processada["decisao_final"],
                "alavancagem_recomendada": acao_final_dict["alavancagem_recomendada"],
                "stop_loss_percent": acao_final_dict["stop_loss"],
                "target": acao_final_dict["target"],
                "justificativa": acao_final_dict["justificativa"]
            },
            
            # 4 Camadas independentes (conforme documentação)
            "dados_camadas": {
                "mercado": {
                    "score": dados_coletados["score_mercado"],
                    "classificacao": dados_mercado["classificacao"],
                    "favoravel": dados_mercado["mercado_favoravel"]  # > 60
                },
                "risco": {
                    "score": dados_coletados["score_risco"],
                    "classificacao": dados_risco["classificacao"],
                    "seguro": dados_risco["posicao_segura"]  # > 50
                },
                "alavancagem": {
                    "max_leverage": dados_coletados["max_leverage_permitida"],
                    "fase_mercado": dados_alavancagem["parametros"]["fase_mercado"],
                    "classificacao": dados_alavancagem["classificacao"]
                },
                "tatico_basico": {
                    "ema_distance": round(dados_coletados["ema_distance"], 1),
                    "rsi_diario": round(dados_coletados["rsi_diario"], 0),
                    "acao_matriz": regra_tatica_basica["acao"],
                    "tamanho_matriz": regra_tatica_basica["tamanho"]
                }
            },
            
            # Análise contextual
            "analise_contextual": {
                "insights": decisao_processada["insights_finais"],
                "confianca_decisao": _avaliar_confianca_integrada(cenario_display) if override_cenario else _avaliar_confianca_matriz_basica(),
                "timing_execucao": _avaliar_timing_integrado(cenario_display) if override_cenario else _avaliar_timing_matriz_basica(),
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
            "alertas": decisao_processada["alertas_finais"],
            
            # Simulação (se disponível)
            "simulacao": simulacao or {
                "status": "indisponivel",
                "motivo": "Dados de posição não encontrados"
            },
            
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na resposta final: {str(e)}")
        raise

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
    elif decisao == "ACUMULAR_SPOT_APENAS":
        tamanho = acao_final.get("tamanho_percent", 75)
        return f"Acumular {tamanho}% APENAS SPOT - {acao_final['justificativa']}"
    else:
        return f"Manter posição atual - {acao_final['justificativa']}"

def _avaliar_confianca_integrada(cenario: dict) -> str:
    """Avalia confiança considerando prioridade do cenário"""
    prioridade = cenario["prioridade"]
    
    if cenario.get("override"):
        return "maxima"
    elif prioridade <= 1:
        return "alta"
    elif prioridade <= 2:
        return "alta"
    else:
        return "media"

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

def _avaliar_confianca_matriz_basica() -> str:
    """Avalia confiança da matriz tática básica"""
    return "media"

def _avaliar_timing_matriz_basica() -> str:
    """Avalia timing da matriz tática básica"""
    return "48_horas"