# app/routers/camada_mercado.py

from fastapi import APIRouter
from datetime import datetime
from app.services.scores import ciclos, momentum, tecnico
import logging

router = APIRouter()

# Pesos conforme especificação v5.0
PESOS_CAMADA_MERCADO = {
    "ciclos": 50,     # 50%
    "tecnico": 30,    # 30% 
    "momentum": 20    # 20%
}

def classificar_mercado(score: float) -> str:
    """Classifica mercado baseado no score"""
    if score >= 60:
        return "favorável"
    elif score >= 40:
        return "neutro"
    else:
        return "desfavorável"

def obter_acao_recomendada(score: float, breakdown: dict) -> str:
    """Determina ação baseada no score e componentes"""
    if score >= 75:
        return "Entrar com alavancagem moderada"
    elif score >= 60:
        return "Entrar com cautela ou manter posição"
    elif score >= 40:
        return "Posição neutra - aguardar melhores sinais"
    elif score >= 25:
        return "Reduzir exposição gradualmente"
    else:
        return "Evitar posições - mercado desfavorável"

def get_market_insights(breakdown: dict) -> list:
    """Gera insights baseados nos componentes"""
    insights = []
    
    # Análise por bloco
    ciclos_score = breakdown.get("ciclos", {}).get("score_ponderado", 0)
    tecnico_score = breakdown.get("tecnico", {}).get("score_ponderado", 0)
    momentum_score = breakdown.get("momentum", {}).get("score_ponderado", 0)
    
    # Insights por força do bloco
    if ciclos_score >= 40:  # 80% de 50 = forte
        insights.append("✅ Indicadores de ciclo favoráveis")
    elif ciclos_score <= 25:  # 50% de 50 = fraco
        insights.append("❌ Indicadores de ciclo desfavoráveis")
    
    if tecnico_score >= 24:  # 80% de 30 = forte
        insights.append("✅ Estrutura técnica sólida")
    elif tecnico_score <= 15:  # 50% de 30 = fraco
        insights.append("❌ Estrutura técnica fraca")
    
    if momentum_score >= 16:  # 80% de 20 = forte
        insights.append("✅ Momentum positivo")
    elif momentum_score <= 10:  # 50% de 20 = fraco
        insights.append("❌ Momentum negativo")
    
    # Divergências
    scores = [ciclos_score/50*10, tecnico_score/30*10, momentum_score/20*10]
    max_score = max(scores)
    min_score = min(scores)
    
    if max_score - min_score > 4:
        insights.append("⚠️ Divergência entre indicadores - cautela recomendada")
    
    return insights

@router.get("/camada-mercado")
async def analisar_mercado():
    """
    API principal da Camada 1: Análise de Mercado
    
    Consolida scores dos blocos Ciclo (50%) + Técnico (30%) + Momentum (20%)
    Retorna se mercado está favorável para posicionamento
    """
    try:
        logging.info("🎯 Iniciando análise Camada Mercado...")
        
        # 1. Buscar scores de todos os blocos
        scores_blocos = {}
        breakdown = {}
        
        for bloco, peso in PESOS_CAMADA_MERCADO.items():
            try:
                if bloco == "ciclos":
                    dados = ciclos.calcular_score()
                elif bloco == "tecnico":
                    dados = tecnico.calcular_score()
                elif bloco == "momentum":
                    dados = momentum.calcular_score()
                
                if dados.get("status") == "success":
                    score_bloco = dados.get("score_consolidado", 0)
                    score_ponderado = (score_bloco * peso) / 100
                    
                    scores_blocos[bloco] = score_bloco
                    breakdown[bloco] = {
                        "score_bruto": score_bloco,
                        "peso": f"{peso}%",
                        "score_ponderado": round(score_ponderado, 2),
                        "classificacao": dados.get("classificacao_consolidada", "unknown"),
                        "status": "✅ OK"
                    }
                else:
                    # Bloco com erro - score 0
                    breakdown[bloco] = {
                        "score_bruto": 0,
                        "peso": f"{peso}%", 
                        "score_ponderado": 0,
                        "classificacao": "erro",
                        "status": f"❌ {dados.get('erro', 'Indisponível')}"
                    }
                    
            except Exception as e:
                logging.error(f"❌ Erro processando {bloco}: {str(e)}")
                breakdown[bloco] = {
                    "score_bruto": 0,
                    "peso": f"{peso}%",
                    "score_ponderado": 0,
                    "classificacao": "erro",
                    "status": f"❌ Erro: {str(e)}"
                }
        
        # 2. Calcular score consolidado da camada
        score_total = sum([b["score_ponderado"] for b in breakdown.values()])
        score_normalizado = min(100, max(0, score_total))  # Garantir 0-100
        
        classificacao = classificar_mercado(score_normalizado)
        acao = obter_acao_recomendada(score_normalizado, breakdown)
        insights = get_market_insights(breakdown)
        
        # 3. Determinar força dos componentes
        componentes_fortes = []
        componentes_fracos = []
        
        for bloco, dados in breakdown.items():
            score_normalizado_bloco = (dados["score_ponderado"] / PESOS_CAMADA_MERCADO[bloco]) * 100
            if score_normalizado_bloco >= 70:
                componentes_fortes.append(bloco.upper())
            elif score_normalizado_bloco <= 40:
                componentes_fracos.append(bloco.upper())
        
        # 4. Resposta consolidada
        return {
            "camada": "mercado",
            "timestamp": datetime.utcnow().isoformat(),
            "score_consolidado": round(score_normalizado, 1),
            "score_maximo": 100,
            "classificacao": classificacao,
            "mercado_favoravel": score_normalizado >= 60,
            "acao_recomendada": acao,
            
            "composicao": {
                "formula": "Score = (Ciclos×50%) + (Técnico×30%) + (Momentum×20%)",
                "calculo": f"Score = {breakdown.get('ciclos', {}).get('score_ponderado', 0)} + {breakdown.get('tecnico', {}).get('score_ponderado', 0)} + {breakdown.get('momentum', {}).get('score_ponderado', 0)} = {score_normalizado:.1f}",
                "breakdown": breakdown
            },
            
            "analise": {
                "componentes_fortes": componentes_fortes,
                "componentes_fracos": componentes_fracos,
                "insights": insights,
                "confiabilidade": "alta" if all(b["status"].startswith("✅") for b in breakdown.values()) else "média"
            },
            
            "proximos_passos": {
                "se_favoravel": "Verificar Camada Risco antes de posicionar",
                "se_neutro": "Aguardar melhores sinais ou manter posição atual",
                "se_desfavoravel": "Evitar novas posições ou reduzir exposição"
            },
            
            "status": "success"
        }
        
    except Exception as e:
        logging.error(f"❌ Erro na análise da camada mercado: {str(e)}")
        return {
            "camada": "mercado",
            "timestamp": datetime.utcnow().isoformat(),
            "score_consolidado": 0,
            "classificacao": "erro",
            "mercado_favoravel": False,
            "acao_recomendada": "Sistema indisponível - não operar",
            "status": "error",
            "erro": str(e)
        }