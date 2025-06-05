# app/services/indicadores/tecnico.py - ATUALIZADO PARA BBW

from datetime import datetime
from app.services.utils.helpers.postgres import get_dados_tecnico
from app.services.utils.helpers.postgres.tecnico_helper import get_emas_detalhadas

def obter_indicadores():
    """
    Retorna indicadores técnicos com EMAs detalhadas por timeframe + BBW
    """
    # Primeiro tenta obter EMAs detalhadas + BBW (novo formato)
    emas_data = get_emas_detalhadas()
    
    if emas_data and "bbw" in emas_data:
        return format_emas_bbw_response(emas_data)
    elif emas_data:
        return format_emas_response(emas_data)
    
    # Fallback para dados legados
    dados_db = get_dados_tecnico()
    
    if dados_db:
        return format_legacy_response(dados_db)
    else:
        return format_no_data_response()

def format_emas_bbw_response(emas_data: dict):
    """Formata resposta com EMAs + BBW (NOVO)"""
    try:
        semanal = emas_data["semanal"]
        diario = emas_data["diario"]
        geral = emas_data["geral"]
        bbw = emas_data["bbw"]
        
        return {
            "bloco": "tecnico",
            "timestamp": geral["timestamp"].isoformat() if geral["timestamp"] else datetime.utcnow().isoformat(),
            "indicadores": {
                "Sistema_EMAs_Semanal": {
                    "valor": get_ema_status_description(semanal["scores"]["consolidado"]),
                    "score_numerico": semanal["scores"]["consolidado"],
                    "peso": "49%",  # 70% de 70% = 49% do bloco total
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
                    "peso": "21%",   # 30% de 70% = 21% do bloco total
                    "fonte": geral["fonte"],
                    "detalhes": {
                        "emas": diario["emas"],
                        "scores": diario["scores"],
                        "alinhamento": diario["scores"]["alinhamento"],
                        "posicao": diario["scores"]["posicao"]
                    }
                },
                "Score_Final_Ponderado": {
                    "valor": get_ema_status_description(geral["score_emas"]),
                    "score_numerico": geral["score_emas"],
                    "peso": "70%",  # 70% do bloco
                    "fonte": geral["fonte"],
                    "ponderacao": "70% semanal + 30% diário"
                },
                "Bollinger_Band_Width": {
                    "valor": f"{bbw['percentage']:.2f}% - {get_bbw_status_description(bbw['percentage'])}",
                    "score_numerico": bbw["score"],
                    "peso": "30%",  # 30% do bloco
                    "fonte": geral["fonte"],
                    "interpretacao": get_bbw_interpretation(bbw["percentage"])
                },
                "Score_Bloco_Final": {
                    "valor": get_ema_status_description(geral["score_bloco_final"]),
                    "score_numerico": geral["score_bloco_final"],
                    "peso": "30%",  # Peso total do bloco técnico
                    "fonte": geral["fonte"],
                    "composicao": "70% EMAs + 30% BBW"
                },
                "BTC_Price": {
                    "valor": f"${geral['btc_price']:,.2f}",
                    "score_numerico": None,
                    "fonte": geral["fonte"]
                }
            },
            "timeframes": {
                "semanal": semanal,
                "diario": diario
            },
            "bbw": bbw,
            "distancias": emas_data.get("distancias", {}),
            "status": "success",
            "fonte_dados": "PostgreSQL_EMAs_BBW_Completo"
        }
        
    except Exception as e:
        return {
            "bloco": "tecnico",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "error",
            "erro": f"Erro formatando EMAs+BBW: {str(e)}",
            "fonte_dados": "PostgreSQL"
        }

def format_emas_response(emas_data: dict):
    """Formata resposta com EMAs detalhadas (sem BBW - compatibilidade)"""
    try:
        semanal = emas_data["semanal"]
        diario = emas_data["diario"]
        geral = emas_data["geral"]
        
        return {
            "bloco": "tecnico",
            "timestamp": geral["timestamp"].isoformat() if geral["timestamp"] else datetime.utcnow().isoformat(),
            "indicadores": {
                "Sistema_EMAs_Semanal": {
                    "valor": get_ema_status_description(semanal["scores"]["consolidado"]),
                    "score_numerico": semanal["scores"]["consolidado"],
                    "peso": "70%",  # 70% de 100% = 70% (sem BBW)
                    "fonte": geral["fonte"],
                    "detalhes": {
                        "emas": semanal["emas"],
                        "scores": semanal["scores"]
                    }
                },
                "Sistema_EMAs_Diario": {
                    "valor": get_ema_status_description(diario["scores"]["consolidado"]),
                    "score_numerico": diario["scores"]["consolidado"], 
                    "peso": "30%",   # 30% de 100% = 30% (sem BBW)
                    "fonte": geral["fonte"],
                    "detalhes": {
                        "emas": diario["emas"],
                        "scores": diario["scores"]
                    }
                },
                "Score_Final_Ponderado": {
                    "valor": get_ema_status_description(geral["score_emas"]),
                    "score_numerico": geral["score_emas"],
                    "peso": "30%",  # Peso total do bloco técnico
                    "fonte": geral["fonte"],
                    "ponderacao": "70% semanal + 30% diário",
                    "observacao": "BBW não disponível neste registro"
                },
                "BTC_Price": {
                    "valor": f"${geral['btc_price']:,.2f}",
                    "score_numerico": None,
                    "fonte": geral["fonte"]
                },
                # Compatibilidade
                "Sistema_EMAs": {
                    "valor": get_ema_status_description(geral["score_emas"]),
                    "score_numerico": geral["score_emas"],
                    "fonte": geral["fonte"]
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
    """Formata resposta com dados legados (compatibilidade total)"""
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
            "BBW": {"valor": None, "fonte": None}
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

def get_bbw_status_description(bbw_percentage: float) -> str:
    """Converte BBW% em descrição"""
    if bbw_percentage < 5:
        return "Compressão Extrema"
    elif bbw_percentage < 10:
        return "Volatilidade Baixa"
    elif bbw_percentage < 20:
        return "Volatilidade Normal"
    elif bbw_percentage < 30:
        return "Volatilidade Alta"
    else:
        return "Volatilidade Extrema"

def get_bbw_interpretation(bbw_percentage: float) -> str:
    """Interpretação tática do BBW"""
    if bbw_percentage < 5:
        return "Breakout iminente - preparar posição"
    elif bbw_percentage < 10:
        return "Mercado em acumulação - aguardar"
    elif bbw_percentage < 20:
        return "Seguir tendência principal"
    elif bbw_percentage < 30:
        return "Reduzir alavancagem - volatilidade alta"
    else:
        return "Evitar novas posições - caos de mercado"

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