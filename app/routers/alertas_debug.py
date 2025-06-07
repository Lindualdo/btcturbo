# app/routers/alertas_debug.py

from fastapi import APIRouter
from datetime import datetime
from app.services.utils.helpers.postgres import get_dados_risco
from app.services.analises.analise_risco import calcular_analise_risco
from app.services.utils.helpers.bbw_calculator import obter_bbw_com_score

router = APIRouter()

@router.get("/alertas/prioritarios-debug")
async def alertas_prioritarios_debug():
    """Debug detalhado dos 5 alertas prioritários"""
    
    debug_info = {
        "timestamp": datetime.utcnow().isoformat(),
        "alertas_ativos": 0,
        "detalhes": {},
        "erros": []
    }
    
    try:
        # 1. Health Factor < 1.3 (CRÍTICO)
        try:
            dados_risco = get_dados_risco()
            if dados_risco:
                hf = float(dados_risco.get("health_factor", 999))
                debug_info["detalhes"]["health_factor_critico"] = {
                    "valor_atual": hf,
                    "threshold": 1.3,
                    "categoria": "CRÍTICO",
                    "status": "🚨 ATIVO" if hf < 1.3 else "✅ OK",
                    "alerta_ativo": hf < 1.3,
                    "acao": "Reduzir 70% posição AGORA"
                }
                if hf < 1.3:
                    debug_info["alertas_ativos"] += 1
        except Exception as e:
            debug_info["erros"].append(f"Health Factor crítico: {str(e)}")
        
        # 2. Score Risco < 30 (CRÍTICO)
        try:
            analise_risco = calcular_analise_risco()
            if analise_risco.get("status") == "success":
                score = analise_risco.get("score_consolidado", 100)
                debug_info["detalhes"]["score_risco_critico"] = {
                    "valor_atual": score,
                    "threshold": 30,
                    "categoria": "CRÍTICO",
                    "status": "🚨 ATIVO" if score < 30 else "✅ OK",
                    "alerta_ativo": score < 30,
                    "acao": "Fechar posição completamente"
                }
                if score < 30:
                    debug_info["alertas_ativos"] += 1
        except Exception as e:
            debug_info["erros"].append(f"Score risco: {str(e)}")
        
        # 3. Health Factor < 1.5 (URGENTE)
        try:
            if dados_risco:
                hf = float(dados_risco.get("health_factor", 999))
                debug_info["detalhes"]["health_factor_urgente"] = {
                    "valor_atual": hf,
                    "threshold": 1.5,
                    "categoria": "URGENTE",
                    "status": "⚠️ ATIVO" if 1.3 <= hf < 1.5 else "✅ OK",
                    "alerta_ativo": 1.3 <= hf < 1.5,
                    "acao": "Preparar redução preventiva"
                }
                if 1.3 <= hf < 1.5:
                    debug_info["alertas_ativos"] += 1
        except Exception as e:
            debug_info["erros"].append(f"Health Factor urgente: {str(e)}")
        
        # 4. Distância Liquidação < 30% (URGENTE)
        try:
            if dados_risco:
                dist_raw = dados_risco.get("dist_liquidacao")
                if dist_raw:
                    dist = float(str(dist_raw).replace("%", ""))
                    debug_info["detalhes"]["distancia_liquidacao"] = {
                        "valor_atual": dist,
                        "threshold": 30,
                        "categoria": "URGENTE",
                        "status": "⚠️ ATIVO" if dist < 30 else "✅ OK",
                        "alerta_ativo": dist < 30,
                        "acao": "Reduzir alavancagem"
                    }
                    if dist < 30:
                        debug_info["alertas_ativos"] += 1
        except Exception as e:
            debug_info["erros"].append(f"Distância liquidação: {str(e)}")
        
        # 5. BBW < 5% há 7+ dias (VOLATILIDADE)
        try:
            bbw_data = obter_bbw_com_score()
            if bbw_data.get("status") == "success":
                bbw = bbw_data["bbw_percentage"]
                dias_comprimido = 0  # Simplificado para debug
                debug_info["detalhes"]["bbw_comprimido"] = {
                    "valor_atual": bbw,
                    "threshold": 5.0,
                    "categoria": "VOLATILIDADE",
                    "status": "⚡ ATIVO" if bbw < 5 and dias_comprimido >= 7 else "✅ OK",
                    "alerta_ativo": bbw < 5 and dias_comprimido >= 7,
                    "dias_comprimido": dias_comprimido,
                    "acao": "Preparar capital para breakout"
                }
                if bbw < 5 and dias_comprimido >= 7:
                    debug_info["alertas_ativos"] += 1
        except Exception as e:
            debug_info["erros"].append(f"BBW: {str(e)}")
        
        # Resumo
        debug_info["resumo"] = {
            "total_prioritarios": 5,
            "alertas_ativos": debug_info["alertas_ativos"],
            "sistema_ok": debug_info["alertas_ativos"] == 0 and len(debug_info["erros"]) == 0,
            "categorias": {
                "criticos": sum(1 for d in debug_info["detalhes"].values() 
                              if d.get("categoria") == "CRÍTICO" and d.get("alerta_ativo")),
                "urgentes": sum(1 for d in debug_info["detalhes"].values() 
                              if d.get("categoria") == "URGENTE" and d.get("alerta_ativo")),
                "volatilidade": sum(1 for d in debug_info["detalhes"].values() 
                                  if d.get("categoria") == "VOLATILIDADE" and d.get("alerta_ativo"))
            }
        }
        
        return debug_info
        
    except Exception as e:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "erro_geral": str(e),
            "sistema_ok": False
        }