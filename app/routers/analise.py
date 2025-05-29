# app/routers/analise.py

from fastapi import APIRouter
from datetime import datetime
from app.services.scores import ciclos, momentum, riscos, tecnico
from app.services import alertas as alertas_service
import logging

router = APIRouter()

@router.get("/analise-btc")
async def analise_btc():
    """API consolidada que retorna análise completa do BTC com scores de todos os blocos"""
    try:
        logging.info("🔄 Iniciando análise consolidada BTC...")
        
        # 1. Buscar scores de todos os blocos
        score_ciclos = ciclos.calcular_score()
        score_momentum = momentum.calcular_score() 
        score_riscos = riscos.calcular_score()
        score_tecnico = tecnico.calcular_score()
        
        # 2. Verificar se todos os blocos têm dados válidos
        blocos_validos = []
        peso_total_disponivel = 0
        
        # Verificar cada bloco e seus pesos
        if score_ciclos.get("status") == "success":
            blocos_validos.append(("ciclos", score_ciclos, 0.40))
            peso_total_disponivel += 0.40
            
        if score_momentum.get("status") == "success":
            blocos_validos.append(("momentum", score_momentum, 0.30))
            peso_total_disponivel += 0.30
            
        if score_riscos.get("status") == "success":
            blocos_validos.append(("riscos", score_riscos, 0.10))
            peso_total_disponivel += 0.10
            
        if score_tecnico.get("status") == "success":
            blocos_validos.append(("tecnico", score_tecnico, 0.20))
            peso_total_disponivel += 0.20
        
        logging.info(f"✅ Blocos válidos encontrados: {len(blocos_validos)}/{4}")
        
        # 3. Calcular score consolidado ponderado
        if peso_total_disponivel > 0:
            score_ponderado = 0
            for nome_bloco, dados_bloco, peso_original in blocos_validos:
                # Normalizar peso baseado no total disponível
                peso_normalizado = peso_original / peso_total_disponivel
                score_bloco = dados_bloco.get("score_consolidado", 0)
                score_ponderado += (score_bloco * peso_normalizado)
                
            score_final = round(score_ponderado, 2)
        else:
            score_final = 0
            logging.warning("⚠️ Nenhum bloco válido encontrado para calcular score")
        
        # 4. Determinar classificação geral
        def classificar_score(score):
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
        
        classificacao_geral = classificar_score(score_final)
        
        # 5. Determinar Kelly allocation baseado no score
        def calcular_kelly(score):
            if score >= 8.0:
                return "75%"
            elif score >= 6.0:
                return "50%"
            elif score >= 4.0:
                return "25%"
            elif score >= 2.0:
                return "10%"
            else:
                return "0%"
        
        kelly_allocation = calcular_kelly(score_final)
        
        # 6. Determinar ação recomendada
        def determinar_acao(score, classificacao):
            if score >= 8.0:
                return "Aumentar posição - condições excepcionais"
            elif score >= 6.0:
                return "Manter posição - condições favoráveis"
            elif score >= 4.0:
                return "Posição neutra - mercado equilibrado"
            elif score >= 2.0:
                return "Reduzir exposição - condições desfavoráveis"
            else:
                return "Zerar alavancagem - risco extremo"
        
        acao_recomendada = determinar_acao(score_final, classificacao_geral)
        
        # 7. Buscar alertas ativos
        try:
            alertas_data = alertas_service.get_alertas()
            alertas_ativos = [alerta["mensagem"] for alerta in alertas_data.get("alertas_ativos", [])]
        except Exception as e:
            logging.error(f"Erro ao buscar alertas: {str(e)}")
            alertas_ativos = ["Sistema de alertas temporariamente indisponível"]
        
        # 8. Preparar pesos dinâmicos (atual: fixos, futuro: baseado em condições de mercado)
        pesos_dinamicos = {
            "ciclo": 0.40,
            "momentum": 0.30,
            "risco": 0.10,
            "tecnico": 0.20
        }
        
        # 9. Estruturar resposta final
        resposta_consolidada = {
            "timestamp": datetime.utcnow().isoformat(),
            "score_final": score_final,
            "score_ajustado": score_final,  # Futuro: aplicar modificador de volatilidade
            "modificador_volatilidade": 1.0,  # Futuro: calcular baseado em BVOL
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
                    "peso": "40%",
                    "status": score_ciclos.get("status", "error")
                },
                "momentum": {
                    "score_consolidado": score_momentum.get("score_consolidado", 0),
                    "classificacao": score_momentum.get("classificacao_consolidada", "N/A"),
                    "peso": "30%",
                    "status": score_momentum.get("status", "error")
                },
                "riscos": {
                    "score_consolidado": score_riscos.get("score_consolidado", 0),
                    "classificacao": score_riscos.get("classificacao_consolidada", "N/A"),
                    "peso": "10%",
                    "status": score_riscos.get("status", "error")
                },
                "tecnico": {
                    "score_consolidado": score_tecnico.get("score_consolidado", 0),
                    "classificacao": score_tecnico.get("classificacao_consolidada", "N/A"),
                    "peso": "20%",
                    "status": score_tecnico.get("status", "error")
                }
            }
        }
        
        logging.info(f"✅ Análise consolidada concluída - Score: {score_final} ({classificacao_geral})")
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