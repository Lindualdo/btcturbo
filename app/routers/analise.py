# app/routers/analise.py

from fastapi import APIRouter, Query
from datetime import datetime
from app.services.scores import ciclos, momentum, riscos, tecnico
from app.services import alertas as alertas_service
import logging

router = APIRouter()

@router.get("/analise-btc")
async def analise_btc(incluir_risco: bool = Query(True, description="Incluir bloco RISCO no cálculo do score final")):
    """API consolidada que retorna análise completa do BTC com scores de todos os blocos"""
    try:
        logging.info(f"🔄 Iniciando análise consolidada BTC - incluir_risco={incluir_risco}...")
        
        # 1. Buscar scores de todos os blocos
        score_ciclos = ciclos.calcular_score()
        score_momentum = momentum.calcular_score() 
        score_riscos = riscos.calcular_score()
        score_tecnico = tecnico.calcular_score()
        
        # 2. Verificar blocos válidos e definir pesos
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
        
        # 3. Calcular score consolidado
        if peso_total_disponivel > 0:
            score_ponderado = 0
            pesos_finais = {}
            
            for nome_bloco, dados_bloco, peso_original in blocos_validos:
                # Normalizar peso baseado no total disponível
                peso_normalizado = peso_original / peso_total_disponivel
                score_bloco = dados_bloco.get("score_consolidado", 0)
                score_ponderado += (score_bloco * peso_normalizado)
                pesos_finais[nome_bloco] = peso_normalizado
                
            score_final = round(score_ponderado, 2)
        else:
            score_final = 0
            pesos_finais = {}
            logging.warning("⚠️ Nenhum bloco válido encontrado para calcular score")
        
        # 4. Determinar classificação e ações
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
        
        # 5. Buscar alertas
        try:
            alertas_data = alertas_service.get_alertas()
            alertas_ativos = [alerta["mensagem"] for alerta in alertas_data.get("alertas_ativos", [])]
        except Exception as e:
            logging.error(f"Erro ao buscar alertas: {str(e)}")
            alertas_ativos = ["Sistema de alertas temporariamente indisponível"]
        
        # 6. Preparar pesos dinâmicos (normalizados)
        pesos_dinamicos = {
            "ciclo": pesos_finais.get("ciclos", 0),
            "momentum": pesos_finais.get("momentum", 0),
            "risco": pesos_finais.get("riscos", 0),
            "tecnico": pesos_finais.get("tecnico", 0)
        }
        
        # 7. Estruturar resposta final
        resposta_consolidada = {
            "timestamp": datetime.utcnow().isoformat(),
            "configuracao": {
                "incluir_risco": incluir_risco,
                "risco_disponivel": risco_disponivel,
                "blocos_no_calculo": len(blocos_validos),
                "nota": "Score calculado SEM risco" if not incluir_risco else "Score calculado COM risco"
            },
            "score_final": score_final,
            "score_ajustado": score_final,  # Futuro: aplicar modificador de volatilidade
            "modificador_volatilidade": 1.0,
            "classificacao_geral": classificacao_geral,
            "kelly_allocation": kelly_allocation,
            "acao_recomendada": acao_recomendada,
            "alertas_ativos": alertas_ativos,
            "pesos_dinamicos": pesos_dinamicos,
            "blocos": {
                "ciclos": score_ciclos,
                "momentum": score_momentum,
                "riscos": score_riscos,  # SEMPRE retorna, independente do incluir_risco
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
        
        logging.info(f"✅ Análise consolidada concluída - Score: {score_final} ({classificacao_geral}) - Risco: {'incluído' if incluir_risco else 'excluído'}")
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