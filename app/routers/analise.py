# app/routers/analise.py - CORRIGIDO v1.0.21 - Dashboard Funcional

from fastapi import APIRouter, Query
from datetime import datetime
from app.services.scores import ciclos, momentum, riscos, tecnico
from app.services import alertas as alertas_service
from app.services.utils.helpers.postgres.scores_consolidados_helper import (
    get_score_cache_diario, save_score_cache_diario
)
import logging

router = APIRouter()

# CONFIGURAÇÃO DOS PESOS v1.0.21
PESOS_BLOCOS = {
    "tecnico": 50,
    "ciclos": 30, 
    "momentum": 20,
    "riscos": 0  # Apenas referência
}

def classificar_score(score: float) -> str:
    """Classificação simplificada"""
    if score >= 8.0: return "ótimo"
    elif score >= 6.0: return "bom"
    elif score >= 4.0: return "neutro"
    elif score >= 2.0: return "ruim"
    else: return "crítico"

def calcular_kelly(score: float) -> str:
    """Kelly Criterion simplificado"""
    if score >= 8.0: return "75%"
    elif score >= 6.0: return "50%" 
    elif score >= 4.0: return "25%"
    elif score >= 2.0: return "10%"
    else: return "0%"

def determinar_acao(score: float) -> str:
    """Ação recomendada simplificada"""
    if score >= 8.0: return "Aumentar posição"
    elif score >= 6.0: return "Manter posição"
    elif score >= 4.0: return "Posição neutra"
    elif score >= 2.0: return "Reduzir exposição"
    else: return "Zerar alavancagem"

def simplificar_alertas(alertas_raw: list) -> list:
    """Simplifica alertas para dashboard"""
    alertas_simples = []
    
    for alerta_obj in alertas_raw:
        if isinstance(alerta_obj, dict):
            msg = alerta_obj.get("mensagem", "")
        else:
            msg = str(alerta_obj)
        
        # Simplificar mensagens longas
        if "Liquidação próxima" in msg:
            alertas_simples.append("Liquidação próxima (HF < 1.15)")
        elif "Funding Rate" in msg and "0.1%" in msg:
            alertas_simples.append("Funding Rate alto (0.1%)")
        elif "EMA200" in msg:
            alertas_simples.append("Mudança de tendência detectada")
        elif "Volatilidade" in msg:
            alertas_simples.append("Volatilidade elevada")
        else:
            # Manter alertas curtos apenas
            if len(msg) < 50:
                alertas_simples.append(msg)
    
    return alertas_simples[:5]  # Máximo 5 alertas

def extrair_dados_bloco(dados_bloco: dict, nome_bloco: str) -> dict:
    """
    CORRIGIDO: Extrai dados com campos compatíveis com Dashboard
    Dashboard espera: score_consolidado e classificacao_consolidada
    """
    if dados_bloco.get("status") != "success":
        return {
            "score_consolidado": 0,           # ← CORRIGIDO: era "score"
            "classificacao_consolidada": "erro",  # ← CORRIGIDO: era "classificacao"
            "peso": PESOS_BLOCOS.get(nome_bloco, 0),
            "status": "erro"
        }
    
    score = dados_bloco.get("score_consolidado", 0)
    classificacao = classificar_score(score)
    
    resultado = {
        "score_consolidado": round(score, 1),     # ← CORRIGIDO: Dashboard compatível
        "classificacao_consolidada": classificacao,  # ← CORRIGIDO: Dashboard compatível
        "peso": PESOS_BLOCOS.get(nome_bloco, 0),
        "status": "ok"
    }
    
    # Adicionar nota específica para riscos
    if nome_bloco == "riscos":
        resultado["nota"] = "Apenas referência"
    
    return resultado

@router.get("/analise-btc")
async def analise_btc_simplificada(
    incluir_risco: bool = Query(False, description="Não usado na v1.0.21 - mantido para compatibilidade"),
    force_update: bool = Query(False, description="Forçar recálculo ignorando cache")
):
    """
    API consolidada v1.0.21 - CORRIGIDA para Dashboard
    
    Correções:
    - Campos compatíveis: score_consolidado, classificacao_consolidada
    - Cache retorna blocos corretamente
    - Cálculo de score usando campos corretos
    """
    try:
        logging.info(f"🔄 Análise BTC v1.0.21 CORRIGIDA - force_update={force_update}")
        
        # 1. VERIFICAR CACHE CORRIGIDO (se não forçar update)
        if not force_update:
            cache_data = get_score_cache_diario(incluir_risco=False)
            if cache_data:
                logging.info(f"✅ Cache encontrado - Score: {cache_data['score_final']}")
                
                # CORRIGIDO: Verificar se dados_completos existe e tem blocos
                dados_cache = cache_data.get('dados_completos', {})
                blocos_cache = dados_cache.get('blocos_simples', {})
                
                # Se cache não tem blocos, forçar recálculo
                if not blocos_cache:
                    logging.warning("⚠️ Cache sem blocos - recalculando...")
                else:
                    # CORRIGIDO: Retornar cache com blocos
                    return {
                        "timestamp": cache_data['timestamp'].isoformat(),
                        "score_final": float(cache_data['score_final']),
                        "classificacao": cache_data['classificacao_geral'],
                        "kelly": cache_data['kelly_allocation'],
                        "acao": cache_data['acao_recomendada'],
                        "alertas": dados_cache.get('alertas_cache', []),
                        "blocos": blocos_cache,  # ← CORRIGIDO: Usar blocos do cache
                        "config": {
                            "versao": "1.0.21",
                            "incluir_risco": False,
                            "fonte": "cache",
                            "data_cache": cache_data['data'].isoformat()
                        }
                    }
        
        # 2. CALCULAR DADOS ATUAIS
        logging.info("🔄 Calculando dados atuais...")
        
        # Buscar scores de todos os blocos
        dados_blocos = {
            "tecnico": tecnico.calcular_score(),
            "ciclos": ciclos.calcular_score(),
            "momentum": momentum.calcular_score(),
            "riscos": riscos.calcular_score()
        }
        
        # 3. CALCULAR SCORE FINAL CORRIGIDO
        score_total = 0
        peso_total = 0
        blocos_simplificados = {}
        
        for nome_bloco, dados in dados_blocos.items():
            bloco_simples = extrair_dados_bloco(dados, nome_bloco)
            blocos_simplificados[nome_bloco] = bloco_simples
            
            # Somar apenas blocos com peso > 0
            if bloco_simples["peso"] > 0 and bloco_simples["status"] == "ok":
                peso_normalizado = bloco_simples["peso"] / 100  # Converter % para decimal
                # CORRIGIDO: Usar score_consolidado em vez de score
                score_total += bloco_simples["score_consolidado"] * peso_normalizado
                peso_total += peso_normalizado
        
        # Score final
        score_final = round(score_total, 1) if peso_total > 0 else 0
        classificacao_final = classificar_score(score_final)
        kelly_final = calcular_kelly(score_final)
        acao_final = determinar_acao(score_final)
        
        # 4. BUSCAR ALERTAS SIMPLIFICADOS
        try:
            alertas_data = alertas_service.get_alertas()
            alertas_raw = alertas_data.get("alertas_ativos", [])
            alertas_simples = simplificar_alertas(alertas_raw)
        except Exception as e:
            logging.error(f"Erro alertas: {str(e)}")
            alertas_simples = ["Sistema de alertas indisponível"]
        
        # 5. RESPOSTA CORRIGIDA
        resposta_final = {
            "timestamp": datetime.utcnow().isoformat(),
            "score_final": score_final,
            "classificacao": classificacao_final,
            "kelly": kelly_final,
            "acao": acao_final,
            "alertas": alertas_simples,
            "blocos": blocos_simplificados,  # ← CORRIGIDO: Sempre retorna blocos
            "config": {
                "versao": "1.0.21",
                "incluir_risco": False,
                "fonte": "fresh_calculation",
                "pesos": "Técnico 50% | Ciclo 30% | Momentum 20%"
            }
        }
        
        # 6. SALVAR CACHE CORRIGIDO
        try:
            # CORRIGIDO: Dados para cache com blocos completos
            dados_cache = {
                "blocos_simples": blocos_simplificados,  # ← CORRIGIDO: Salvar blocos no cache
                "alertas_cache": alertas_simples
            }
            
            save_score_cache_diario(
                score_final=score_final,
                classificacao_geral=classificacao_final,
                kelly_allocation=kelly_final,
                acao_recomendada=acao_final,
                pesos_dinamicos={"versao": "1.0.21", "simplificado": True},
                dados_completos=dados_cache,  # ← CORRIGIDO: Incluir blocos no cache
                incluir_risco=False
            )
            logging.info(f"✅ Cache corrigido salvo - Score: {score_final}")
        except Exception as e:
            logging.error(f"⚠️ Falha ao salvar cache: {str(e)}")
        
        logging.info(f"✅ Análise v1.0.21 CORRIGIDA concluída - Score: {score_final} ({classificacao_final})")
        return resposta_final
        
    except Exception as e:
        logging.error(f"❌ Erro na análise: {str(e)}")
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "score_final": 0,
            "classificacao": "erro",
            "kelly": "0%",
            "acao": "Sistema indisponível",
            "alertas": [f"Erro: {str(e)}"],
            "blocos": {},  # ← Vazio em caso de erro
            "config": {
                "versao": "1.0.21",
                "incluir_risco": False,
                "fonte": "error",
                "erro": str(e)
            }
        }