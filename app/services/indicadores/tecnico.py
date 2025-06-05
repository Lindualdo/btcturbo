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
    
    if emas_data:
        # Verificar se tem BBW válido (não nulo e não zero)
        bbw_data = emas_data.get("bbw", {})
        has_valid_bbw = (
            bbw_data and 
            bbw_data.get("percentage") is not None and 
            bbw_data.get("score") is not None and
            bbw_data.get("percentage") > 0
        )
        
        if has_valid_bbw:
            return format_emas_bbw_response(emas_data)
        else:
            return format_emas_response(emas_data)
    
    # Fallback para dados legados
    dados_db = get_dados_tecnico()
    
    if dados_db:
        return format_legacy_response(dados_db)
    else:
        return format_no_data_response()

def format_emas_bbw_response(emas_data: dict):
    """Formata resposta com EMAs + BBW organizada"""
    try:
        semanal = emas_data["semanal"]
        diario = emas_data["diario"]
        geral = emas_data["geral"]
        bbw = emas_data["bbw"]
        distancias = emas_data.get("distancias", {})
        
        # Calcular score final do bloco
        score_emas = geral["score_emas"]
        score_bbw = bbw["score"]
        score_consolidado = (score_emas * 0.7) + (score_bbw * 0.3)
        
        return {
            "bloco": "tecnico",
            "peso_bloco": "30%",
            "score_consolidado": round(score_consolidado, 2),
            "classificacao_consolidada": get_ema_status_description(score_consolidado),
            "timestamp": geral["timestamp"].isoformat() if geral["timestamp"] else datetime.utcnow().isoformat(),
            
            "indicadores": {
                "Sistema_EMAs": {
                    "valor": get_ema_status_description(score_emas),
                    "score": score_emas,
                    "peso": "70%",
                    "fonte": geral["fonte"],
                    "detalhes": {
                        "semanal": {
                            "peso": "70%",
                            "score_total": semanal["scores"]["consolidado"],
                            "alinhamento": {
                                "score": semanal["scores"]["alinhamento"],
                                "peso": "50%"
                            },
                            "posicao": {
                                "score": semanal["scores"]["posicao"],
                                "peso": "50%"
                            },
                            "emas": semanal["emas"],
                            "distancias": distancias.get("weekly", {})
                        },
                        "diario": {
                            "peso": "30%",
                            "score_total": diario["scores"]["consolidado"],
                            "alinhamento": {
                                "score": diario["scores"]["alinhamento"],
                                "peso": "50%"
                            },
                            "posicao": {
                                "score": diario["scores"]["posicao"],
                                "peso": "50%"
                            },
                            "emas": diario["emas"],
                            "distancias": distancias.get("daily", {})
                        },
                        "calculo": f"Score = ({semanal['scores']['consolidado']} × 0.7) + ({diario['scores']['consolidado']} × 0.3) = {score_emas}"
                    }
                },
                
                "Bollinger_Band_Width": {
                    "valor": f"{bbw['percentage']:.2f}% - {get_bbw_status_description(bbw['percentage'])}",
                    "score": score_bbw,
                    "peso": "30%",
                    "fonte": geral["fonte"],
                    "detalhes": {
                        "bbw_percentage": bbw["percentage"],
                        "interpretacao": get_bbw_interpretation(bbw["percentage"]),
                        "acao_recomendada": get_bbw_action(bbw["percentage"]),
                        "timeframe_esperado": get_bbw_timeframe(bbw["percentage"]),
                        "bollinger_bands": distancias.get("bbw", {}).get("bands", {})
                    }
                }
            },
            
            "calculo_final": {
                "formula": "Score = (EMAs × 0.7) + (BBW × 0.3)",
                "substituicao": f"Score = ({score_emas} × 0.7) + ({score_bbw} × 0.3)",
                "resultado": f"Score = {score_emas * 0.7:.3f} + {score_bbw * 0.3:.3f} = {score_consolidado:.2f}"
            },
            
            "btc_price": geral["btc_price"],
            "alertas": generate_organized_alerts(score_consolidado, semanal, diario, bbw, distancias),
            "status": "success"
        }
        
    except Exception as e:
        return {
            "bloco": "tecnico",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "error",
            "erro": f"Erro formatando EMAs+BBW: {str(e)}"
        }

def get_bbw_action(bbw_percentage: float) -> str:
    """Ação recomendada baseada no BBW"""
    if bbw_percentage < 5:
        return "Preparar para breakout - aguardar direção"
    elif bbw_percentage < 10:
        return "Posição neutra - aguardar sinais"
    elif bbw_percentage < 20:
        return "Seguir tendência principal"
    elif bbw_percentage < 30:
        return "Reduzir alavancagem - cautela"
    else:
        return "Evitar novas posições - volatilidade extrema"

def get_bbw_timeframe(bbw_percentage: float) -> str:
    """Timeframe esperado para mudança"""
    if bbw_percentage < 5:
        return "1-7 dias"
    elif bbw_percentage < 10:
        return "1-2 semanas"
    elif bbw_percentage < 20:
        return "Indefinido"
    elif bbw_percentage < 30:
        return "Alguns dias"
    else:
        return "Até normalizar"

def generate_organized_alerts(score_final: float, semanal: dict, diario: dict, bbw: dict, distancias: dict) -> list:
    """Gera alertas organizados e relevantes"""
    alerts = []
    
    try:
        # Alertas de score crítico
        if score_final < 4:
            alerts.append("🚨 Score técnico crítico - Sair da posição")
        elif score_final < 6:
            alerts.append("⚠️ Score técnico baixo - Reduzir alavancagem")
        
        # Alertas de alinhamento
        if semanal["scores"]["alinhamento"] == 10:
            alerts.append("✅ Alinhamento EMAs semanal perfeito - Estrutura bullish")
        elif semanal["scores"]["alinhamento"] < 6:
            alerts.append("📉 Alinhamento EMAs semanal quebrado - Risco de reversão")
        
        # Alertas BBW
        bbw_pct = bbw["percentage"]
        if bbw_pct < 5:
            alerts.append(f"🎯 BBW comprimido ({bbw_pct:.1f}%) - Breakout iminente")
        elif bbw_pct > 30:
            alerts.append(f"🌪️ BBW extremo ({bbw_pct:.1f}%) - Volatilidade perigosa")
        
        # Alertas de distância (weekly)
        weekly_dist = distancias.get("weekly", {})
        for ema, dist_str in weekly_dist.items():
            if "%" in str(dist_str):
                try:
                    dist_pct = float(str(dist_str).replace("%", "").replace("+", ""))
                    if dist_pct > 100 and "610" in ema:
                        alerts.append(f"🔥 Muito esticado da {ema.upper()} ({dist_pct:+.0f}%) - Pullback provável")
                except:
                    continue
        
        return alerts[:4]  # Máximo 4 alertas
        
    except Exception as e:
        return [f"⚠️ Erro gerando alertas: {str(e)}"]

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