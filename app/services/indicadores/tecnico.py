# app/services/indicadores/tecnico.py

from datetime import datetime
from app.services.utils.helpers.postgres import get_dados_tecnico
from app.services.utils.helpers.postgres.tecnico_helper import get_emas_detalhadas

def obter_indicadores():
    """
    Retorna indicadores técnicos com EMAs detalhadas por timeframe
    """
    # Primeiro tenta obter EMAs detalhadas (novo formato)
    emas_data = get_emas_detalhadas()
    
    if emas_data:
        return format_emas_response(emas_data)
    
    # Fallback para dados legados
    dados_db = get_dados_tecnico()
    
    if dados_db:
        return format_legacy_response(dados_db)
    else:
        return format_no_data_response()

def format_emas_response(emas_data: dict):
    """Formata resposta com EMAs detalhadas - CORRIGIDO"""
    try:
        semanal = emas_data["semanal"]
        diario = emas_data["diario"]
        geral = emas_data["geral"]
        
        # CORREÇÃO: Acessar score do local correto
        score_final_ponderado = geral.get("score_final_ponderado", 0.0)
        
        return {
            "bloco": "tecnico",
            "timestamp": geral["timestamp"].isoformat() if geral["timestamp"] else datetime.utcnow().isoformat(),
            "indicadores": {
                "Sistema_EMAs_Semanal": {
                    "valor": get_ema_status_description(semanal["scores"]["consolidado"]),
                    "score_numerico": semanal["scores"]["consolidado"],
                    "peso": "14%",  # 70% de 20% = 14%
                    "fonte": geral["fonte"],
                    "detalhes": {
                        "emas": semanal["emas"],
                        "scores": semanal["scores"],
                        "alinhamento": semanal["scores"]["alinhamento"],
                        "posicao": semanal["scores"]["posicao"]
                    }
                },
                "Sistema_EMAs_Diario": {
                    "valor": get_ema_status_description(diario["scores"]["consolidado"]),
                    "score_numerico": diario["scores"]["consolidado"],
                    "peso": "6%",   # 30% de 20% = 6%
                    "fonte": geral["fonte"],
                    "detalhes": {
                        "emas": diario["emas"],
                        "scores": diario["scores"],
                        "alinhamento": diario["scores"]["alinhamento"],
                        "posicao": diario["scores"]["posicao"]
                    }
                },
                "Score_Final_Ponderado": {
                    "valor": get_ema_status_description(score_final_ponderado),
                    "score_numerico": score_final_ponderado,
                    "peso": "20%",
                    "fonte": geral["fonte"],
                    "ponderacao": "70% semanal + 30% diário"
                },
                "Padroes_Graficos": {
                    "valor": "Descontinuado",
                    "score_numerico": 0.0,
                    "fonte": geral["fonte"],
                    "observacao": "Peso zerado - EMAs são o foco principal"
                }
            },
            "timeframes": {
                "semanal": semanal,
                "diario": diario
            },
            "distancias": emas_data.get("distancias", {}),
            "status": "success",
            "fonte_dados": "PostgreSQL_EMAs_Detalhadas"
        }
        
    except Exception as e:
        return {
            "bloco": "tecnico",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "error",
            "erro": f"Erro formatando EMAs: {str(e)}",
            "fonte_dados": "PostgreSQL"
        }

def format_legacy_response(dados_db: dict):
    """Formata resposta com dados legados (compatibilidade)"""
    try:
        sistema_emas_score = float(dados_db["sistema_emas"]) if dados_db["sistema_emas"] else 0.0
        padroes_score = float(dados_db["padroes_graficos"]) if dados_db["padroes_graficos"] else 0.0
        
        return {
            "bloco": "tecnico", 
            "timestamp": dados_db["timestamp"].isoformat() if dados_db["timestamp"] else datetime.utcnow().isoformat(),
            "indicadores": {
                "Sistema_EMAs": {
                    "valor": get_ema_status_description(sistema_emas_score),
                    "score_numerico": sistema_emas_score,
                    "fonte": dados_db["fonte"] or "PostgreSQL"
                },
                "Padroes_Graficos": {
                    "valor": get_pattern_status_description(padroes_score),
                    "score_numerico": padroes_score,
                    "fonte": dados_db["fonte"] or "PostgreSQL"
                }
            },
            "status": "success",
            "fonte_dados": "PostgreSQL_Legacy"
        }
        
    except Exception as e:
        return {
            "bloco": "tecnico",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "error", 
            "erro": f"Erro dados legados: {str(e)}",
            "fonte_dados": "PostgreSQL"
        }

def format_no_data_response():
    """Resposta quando não há dados"""
    return {
        "bloco": "tecnico",
        "timestamp": datetime.utcnow().isoformat(),
        "indicadores": {
            "Sistema_EMAs": {"valor": None, "fonte": None},
            "Padroes_Graficos": {"valor": None, "fonte": None}
        },
        "status": "no_data",
        "fonte_dados": "PostgreSQL"
    }

def get_ema_status_description(score: float) -> str:
    """Converte score numérico EMAs em descrição"""
    if score >= 8.1:
        return "Tendência Forte"
    elif score >= 6.1:
        return "Correção Saudável"
    elif score >= 4.1:
        return "Neutro/Transição"
    elif score >= 2.1:
        return "Reversão Iminente"
    else:
        return "Bear Confirmado"

def get_pattern_status_description(score: float) -> str:
    """Converte score padrões em descrição (legado)"""
    if score >= 7.0:
        return "Bull Flag/Ascending Triangle"
    elif score >= 5.0:
        return "Neutro/Sem Padrão"
    elif score >= 3.0:
        return "Bear Flag/Descending Triangle"
    else:
        return "Head & Shoulders/Double Top"