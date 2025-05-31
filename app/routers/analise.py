# app/routers/analise.py

from fastapi import APIRouter, Query
from datetime import datetime, date
from app.services.scores import ciclos, momentum, riscos, tecnico
from app.services import alertas as alertas_service
from app.services.utils.helpers.postgres.scores_consolidados_helper import (
    get_score_cache_diario, save_score_cache_diario
)
import logging

router = APIRouter()

@router.get("/analise-btc")
async def analise_btc(
    incluir_risco: bool = Query(True, description="Incluir bloco RISCO no cálculo do score final"),
    force_update: bool = Query(False, description="Forçar recálculo ignorando cache")
):
    """API consolidada que retorna análise completa do BTC com cache diário"""
    try:
        logging.info(f"🔄 Análise BTC - incluir_risco={incluir_risco}, force_update={force_update}")
        
        # 1. VERIFICAR CACHE PRIMEIRO (se não forçar update)
        if not force_update:
            cache_data = get_score_cache_diario(incluir_risco=incluir_risco)
            if cache_data:
                logging.info(f"✅ Usando cache - Score: {cache_data['score_final']}")
                
                # Montar resposta do cache
                resposta_cache = {
                    "timestamp": cache_data['timestamp'].isoformat(),
                    "configuracao": {
                        "incluir_risco": cache_data['incluir_risco'],
                        "fonte": "cache",
                        "data_cache": cache_data['data'].isoformat(),
                        "nota": f"Dados em cache para {cache_data['data']} - Use force_update=true para recalcular"
                    },
                    "score_final": float(cache_data['score_final']),
                    "score_ajustado": float(cache_data['score_final']),
                    "modificador_volatilidade": 1.0,
                    "classificacao_geral": cache_data['classificacao_geral'],
                    "kelly_allocation": cache_data['kelly_allocation'],
                    "acao_recomendada": cache_data['acao_recomendada'],
                    "alertas_ativos": ["Cache ativo - Use force_update para dados atuais"],
                    "pesos_dinamicos": cache_data['pesos_dinamicos'] or {},
                    "blocos": cache_data['dados_completos'].get('blocos', {}) if cache_data['dados_completos'] else {},
                    "resumo_blocos": cache_data['dados_completos'].get('resumo_blocos', {}) if cache_data['dados_completos'] else {}
                }
                
                return resposta_cache
        
        # 2. CALCULAR FRESH DATA (quando não há cache ou force_update=True)
        logging.info("🔄 Calculando dados frescos via APIs...")
        
        # Buscar scores de todos os blocos
        score_ciclos = ciclos.calcular_score()
        score_momentum = momentum.calcular_score() 
        score_riscos = riscos.calcular_score()
        score_tecnico = tecnico.calcular_score()
        
        # Verificar blocos válidos e definir pesos
        blocos_validos = []
        peso_total_disponivel = 0
        
        # Pesos originais
        peso_ciclo_original = 0.40
        peso_momentum_original = 0.30
        peso_risco_original = 0.10
        peso_tecnico_original = 0.20
        
        # Verificar cada bloco
        if score_ciclos.get("status") == "success":
            blocos_validos.append(("ciclos", score_ciclos, peso_ciclo_original))
            peso_total_disponivel += peso_ciclo_original
            
        if score_momentum.get("status") == "success":
            blocos_validos.append(("momentum", score_momentum, peso_momentum_original))
            peso_total_disponivel += peso_momentum_original
            
        if score_tecnico.get("status") == "success":
            blocos_validos.append(("tecnico", score_tecnico, peso_tecnico_original))
            peso_total_disponivel += peso_tecnico_original
        
        # RISCO: só incluir no cálculo se incluir_risco=True
        risco_disponivel = score_riscos.get("status") == "success"
        if incluir_risco and risco_disponivel:
            blocos_validos.append(("riscos", score_riscos, peso_risco_original))
            peso_total_disponivel += peso_risco_original
        
        logging.info(f"✅ Blocos no cálculo: {len(blocos_validos)} - Peso total: {peso_total_disponivel}")
        
        # Calcular score consolidado
        if peso_total_disponivel > 0:
            score_ponderado = 0
            pesos_finais = {}
            
            for nome_bloco, dados_bloco, peso_original in blocos_validos:
                peso_normalizado = peso_original / peso_total_disponivel
                score_bloco = dados_bloco.get("score_consolidado", 0)
                score_ponderado += (score_bloco * peso_normalizado)
                pesos_finais[nome_bloco] = peso_normalizado
                
            score_final = round(score_ponderado, 2)
        else:
            score_final = 0
            pesos_finais = {}
            logging.warning("⚠️ Nenhum bloco válido encontrado para calcular score")
        
        # Determinar classificação e ações
        def classificar_score(score):
            if score >= 8.0: return "ótimo"
            elif score >= 6.0: return "bom"
            elif score >= 4.0: return "neutro"
            elif score >= 2.0: return "ruim"
            else: return "crítico"
        
        def calcular_kelly(score):
            if score >= 8.0: return "75%"
            elif score >= 6.0: return "50%"
            elif score >= 4.0: return "25%"
            elif score >= 2.0: return "10%"
            else: return "0%"
        
        def determinar_acao(score):
            if score >= 8.0: return "Aumentar posição - condições excepcionais"
            elif score >= 6.0: return "Manter posição - condições favoráveis"
            elif score >= 4.0: return "Posição neutra - mercado equilibrado"
            elif score >= 2.0: return "Reduzir exposição - condições desfavoráveis"
            else: return "Zerar alavancagem - risco extremo"
        
        classificacao_geral = classificar_score(score_final)
        kelly_allocation = calcular_kelly(score_final)
        acao_recomendada = determinar_acao(score_final)
        
        # Buscar alertas
        try:
            alertas_data = alertas_service.get_alertas()
            alertas_ativos = [alerta["mensagem"] for alerta in alertas_data.get("alertas_ativos", [])]
        except Exception as e:
            logging.error(f"Erro ao buscar alertas: {str(e)}")
            alertas_ativos = ["Sistema de alertas temporariamente indisponível"]
        
        # Preparar pesos dinâmicos
        pesos_dinamicos = {
            "ciclo": pesos_finais.get("ciclos", 0),
            "momentum": pesos_finais.get("momentum", 0),
            "risco": pesos_finais.get("riscos", 0),
            "tecnico": pesos_finais.get("tecnico", 0)
        }
        
        # Estruturar resposta final
        resposta_consolidada = {
            "timestamp": datetime.utcnow().isoformat(),
            "configuracao": {
                "incluir_risco": incluir_risco,
                "risco_disponivel": risco_disponivel,
                "blocos_no_calculo": len(blocos_validos),
                "fonte": "fresh_calculation",
                "force_update": force_update,
                "nota": "Score calculado SEM risco" if not incluir_risco else "Score calculado COM risco"
            },
            "score_final": score_final,
            "score_ajustado": score_final,
            "modificador_volatilidade": 1.0,
            "classificacao_geral": classificacao_geral,
            "kelly_allocation": kelly_allocation,
            "acao_recomendada": acao_recomendada,
            "alertas_ativos": alertas_ativos,
            "pesos_dinamicos": pesos_dinamicos,
            "blocos": {
                "ciclos": score_ciclos,
                "momentum": score_momentum,
                "riscos": score_riscos,
                "tecnico": score_tecnico
            },
            "resumo_blocos": {
                "ciclos": {
                    "score_consolidado": score_ciclos.get("score_consolidado", 0),
                    "classificacao": score_ciclos.get("classificacao_consolidada", "N/A"),
                    "peso": f"{pesos_dinamicos['ciclo']*100:.1f}%",
                    "status": score_ciclos.get("status", "error"),
                    "incluido_no_calculo": "ciclos" in [b[0] for b in blocos_validos]
                },
                "momentum": {
                    "score_consolidado": score_momentum.get("score_consolidado", 0),
                    "classificacao": score_momentum.get("classificacao_consolidada", "N/A"),
                    "peso": f"{pesos_dinamicos['momentum']*100:.1f}%",
                    "status": score_momentum.get("status", "error"),
                    "incluido_no_calculo": "momentum" in [b[0] for b in blocos_validos]
                },
                "riscos": {
                    "score_consolidado": score_riscos.get("score_consolidado", 0),
                    "classificacao": score_riscos.get("classificacao_consolidada", "N/A"),
                    "peso": f"{pesos_dinamicos['risco']*100:.1f}%",
                    "status": score_riscos.get("status", "error"),
                    "incluido_no_calculo": "riscos" in [b[0] for b in blocos_validos]
                },
                "tecnico": {
                    "score_consolidado": score_tecnico.get("score_consolidado", 0),
                    "classificacao": score_tecnico.get("classificacao_consolidada", "N/A"),
                    "peso": f"{pesos_dinamicos['tecnico']*100:.1f}%",
                    "status": score_tecnico.get("status", "error"),
                    "incluido_no_calculo": "tecnico" in [b[0] for b in blocos_validos]
                }
            }
        }
        
        # 3. SALVAR NO CACHE para próximas consultas
        try:
            save_score_cache_diario(
                score_final=score_final,
                classificacao_geral=classificacao_geral,
                kelly_allocation=kelly_allocation,
                acao_recomendada=acao_recomendada,
                pesos_dinamicos=pesos_dinamicos,
                dados_completos=resposta_consolidada,
                incluir_risco=incluir_risco
            )
            logging.info(f"✅ Cache salvo para hoje - Score: {score_final}")
        except Exception as e:
            logging.error(f"⚠️ Falha ao salvar cache: {str(e)}")
        
        logging.info(f"✅ Análise concluída - Score: {score_final} ({classificacao_geral})")
        return resposta_consolidada
        
    except Exception as e:
        logging.error(f"❌ Erro na análise consolidada: {str(e)}")
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "error",
            "erro": f"Falha na análise consolidada: {str(e)}",
            "score_final": 0,
            "classificacao_geral": "erro",
            "kelly_allocation": "0%",
            "acao_recomendada": "Sistema indisponível - aguarde correção"
        }