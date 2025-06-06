# app/routers/analise_risco.py - CORRIGIDA

from fastapi import APIRouter
from datetime import datetime
from app.services.scores import riscos
import logging

router = APIRouter()

def classificar_risco(score: float) -> str:
    """Classifica risco baseado no score"""
    if score >= 70:
        return "seguro"
    elif score >= 50:
        return "moderado"
    else:
        return "crítico"

def obter_acao_recomendada(score: float) -> str:
    """Determina ação baseada no score de risco"""
    if score >= 80:
        return "Posição segura - pode aumentar alavancagem"
    elif score >= 70:
        return "Posição segura - manter atual"
    elif score >= 50:
        return "Risco moderado - reduzir alavancagem"
    elif score >= 30:
        return "Alto risco - reduzir 50% da posição"
    else:
        return "PERIGO - fechar posição imediatamente"

@router.get("/analise-risco")
async def analisar_risco():
    """
    API principal da Camada 2: Gestão de Risco
    
    Usa dados já calculados de /calcular-score/riscos
    """
    try:
        logging.info("🛡️ Iniciando análise Camada Risco...")
        
        # 1. Usar service existente que já calcula tudo
        dados_riscos = riscos.calcular_score()
        
        if dados_riscos.get("status") != "success":
            return {
                "analise": "risco",
                "timestamp": datetime.utcnow().isoformat(),
                "score_consolidado": 0,
                "classificacao": "erro",
                "posicao_segura": False,
                "acao_recomendada": "Sistema indisponível - não operar",
                "status": "error",
                "erro": dados_riscos.get("erro", "Dados indisponíveis")
            }
        
        # 2. Extrair score já calculado (base 10 → base 100)
        score_base_10 = dados_riscos.get("score_consolidado", 0)
        score_consolidado = score_base_10 * 10
        
        # 3. Usar breakdown existente
        indicadores = dados_riscos.get("indicadores", {})
        breakdown = {
            "health_factor": {
                "score_bruto": indicadores.get("Health_Factor", {}).get("score", 0) * 10,
                "peso": "50%",
                "score_ponderado": indicadores.get("Health_Factor", {}).get("score", 0) * 5,
                "valor_display": indicadores.get("Health_Factor", {}).get("valor", "N/A"),
                "classificacao": indicadores.get("Health_Factor", {}).get("classificacao", "unknown"),
                "status": "✅ OK"
            },
            "dist_liquidacao": {
                "score_bruto": indicadores.get("Dist_Liquidacao", {}).get("score", 0) * 10,
                "peso": "50%",
                "score_ponderado": indicadores.get("Dist_Liquidacao", {}).get("score", 0) * 5,
                "valor_display": indicadores.get("Dist_Liquidacao", {}).get("valor", "N/A"),
                "classificacao": indicadores.get("Dist_Liquidacao", {}).get("classificacao", "unknown"),
                "status": "✅ OK"
            }
        }
        
        classificacao = classificar_risco(score_consolidado)
        acao = obter_acao_recomendada(score_consolidado)
        
        # 4. Resposta consolidada
        return {
            "analise": "risco",
            "timestamp": dados_riscos.get("timestamp", datetime.utcnow().isoformat()),
            "score_consolidado": round(score_consolidado, 1),
            "score_maximo": 100,
            "classificacao": classificacao,
            "posicao_segura": score_consolidado >= 50,
            "acao_recomendada": acao,
            
            "composicao": {
                "formula": "Score = (Health Factor×50%) + (Dist.Liquidação×50%)",
                "calculo": f"Score = {breakdown['health_factor']['score_ponderado']} + {breakdown['dist_liquidacao']['score_ponderado']} = {score_consolidado:.1f}",
                "breakdown": breakdown
            },
            
            "status": "success"
        }
        
    except Exception as e:
        logging.error(f"❌ Erro na análise da camada risco: {str(e)}")
        return {
            "analise": "risco",
            "timestamp": datetime.utcnow().isoformat(),
            "score_consolidado": 0,
            "classificacao": "erro",
            "posicao_segura": False,
            "acao_recomendada": "Sistema indisponível - não operar",
            "status": "error",
            "erro": str(e)
        }