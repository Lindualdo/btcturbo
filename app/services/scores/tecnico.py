# app/services/scores/tecnico.py - REFATORADO COM BBW

from app.services.indicadores import tecnico as indicadores_tecnico

def interpretar_classificacao(score):
    """Converte score numérico em classificação"""
    if score >= 8.1:
        return "Tendência Forte"
    elif score >= 6.1:
        return "Correção Saudável"
    elif score >= 4.1:
        return "Neutro"
    elif score >= 2.1:
        return "Reversão"
    else:
        return "Bear Confirmado"

def calcular_score():
    """
    Calcula score consolidado do bloco TÉCNICO usando dados já processados
    REFATORADO: usa estrutura organizada com EMAs + BBW
    """
    # 1. Obter dados brutos da API
    dados_indicadores = indicadores_tecnico.obter_indicadores()
    
    if dados_indicadores.get("status") != "success":
        return {
            "bloco": "tecnico",
            "status": "error",
            "erro": "Dados não disponíveis"
        }
    
    indicadores = dados_indicadores["indicadores"]
    
    # 2. Verificar qual estrutura temos
    if "Sistema_EMAs" in indicadores and "Bollinger_Band_Width" in indicadores:
        return calcular_score_com_bbw(dados_indicadores)
    elif "Score_Final_Ponderado" in indicadores:
        return calcular_score_emas_detalhadas(dados_indicadores)
    else:
        return calcular_score_legado(dados_indicadores)

def calcular_score_com_bbw(dados_indicadores):
    """
    NOVO: Usa score já calculado na coleta (EMAs + BBW)
    """
    try:
        indicadores = dados_indicadores["indicadores"]
        
        # Extrair scores dos componentes
        score_emas = indicadores["Sistema_EMAs"]["score"]
        score_bbw = indicadores["Bollinger_Band_Width"]["score"]
        
        # Calcular score final do bloco
        score_consolidado = (score_emas * 0.7) + (score_bbw * 0.3)
        
        return {
            "bloco": "tecnico",
            "peso_bloco": "40%",
            "score_consolidado": round(score_consolidado, 2),
            "classificacao_consolidada": interpretar_classificacao(score_consolidado),
            "timestamp": dados_indicadores["timestamp"],
            "metodo": "emas_bbw_completo",
            
            # Indicadores principais
            "indicadores": {
                "Sistema_EMAs": {
                    "valor": indicadores["Sistema_EMAs"]["valor"],
                    "score": score_emas,
                    "peso": "70%",
                    "fonte": indicadores["Sistema_EMAs"]["fonte"]
                },
                "Bollinger_Band_Width": {
                    "valor": indicadores["Bollinger_Band_Width"]["valor"],
                    "score": score_bbw,
                    "peso": "30%",
                    "fonte": indicadores["Bollinger_Band_Width"]["fonte"]
                }
            },
            
            "calculo_final": {
                "formula": "Score = (EMAs × 0.7) + (BBW × 0.3)",
                "substituicao": f"Score = ({score_emas} × 0.7) + ({score_bbw} × 0.3)",
                "resultado": f"Score = {score_emas * 0.7:.3f} + {score_bbw * 0.3:.3f} = {score_consolidado:.2f}"
            },
            
            "status": "success"
        }
        
    except Exception as e:
        return {
            "bloco": "tecnico",
            "status": "error",
            "erro": f"Erro score BBW: {str(e)}"
        }

def calcular_score_emas_detalhadas(dados_indicadores):
    """
    Sistema EMAs detalhadas (sem BBW - compatibilidade)
    """
    try:
        indicadores = dados_indicadores["indicadores"]
        timeframes = dados_indicadores.get("timeframes", {})
        
        # Score final EMAs (sem BBW)
        score_final = indicadores["Score_Final_Ponderado"]["score_numerico"]
        
        return {
            "bloco": "tecnico",
            "peso_bloco": "30%",
            "score_consolidado": round(score_final, 2),
            "classificacao_consolidada": interpretar_classificacao(score_final),
            "timestamp": dados_indicadores["timestamp"],
            "metodo": "emas_multitimeframe",
            "timeframes": {
                "semanal": {
                    "peso": "70%",
                    "score_total": timeframes.get("semanal", {}).get("scores", {}).get("consolidado", 0),
                    "alinhamento": timeframes.get("semanal", {}).get("scores", {}).get("alinhamento", 0),
                    "posicao": timeframes.get("semanal", {}).get("scores", {}).get("posicao", 0),
                    "emas": timeframes.get("semanal", {}).get("emas", {})
                },
                "diario": {
                    "peso": "30%", 
                    "score_total": timeframes.get("diario", {}).get("scores", {}).get("consolidado", 0),
                    "alinhamento": timeframes.get("diario", {}).get("scores", {}).get("alinhamento", 0),
                    "posicao": timeframes.get("diario", {}).get("scores", {}).get("posicao", 0),
                    "emas": timeframes.get("diario", {}).get("emas", {})
                }
            },
            "indicadores": {
                "Sistema_EMAs_Multitimeframe": {
                    "valor": indicadores["Score_Final_Ponderado"]["valor"],
                    "score": round(score_final, 1),
                    "classificacao": interpretar_classificacao(score_final),
                    "peso": "30%",
                    "fonte": indicadores["Score_Final_Ponderado"]["fonte"],
                    "ponderacao": "70% semanal + 30% diário"
                },
                "BBW": {
                    "valor": "Não disponível",
                    "score": 0.0,
                    "classificacao": "N/A",
                    "peso": "0%",
                    "observacao": "BBW não coletado neste registro"
                }
            },
            "distancias": dados_indicadores.get("distancias", {}),
            "alertas": generate_technical_alerts(score_final, timeframes),
            "status": "success"
        }
        
    except Exception as e:
        return {
            "bloco": "tecnico",
            "status": "error",
            "erro": f"Erro EMAs detalhadas: {str(e)}"
        }

def calcular_score_legado(dados_indicadores):
    """
    Sistema legado (compatibilidade total)
    """
    try:
        indicadores = dados_indicadores["indicadores"]
        
        # Extrair scores já calculados
        emas_score_num = indicadores["Sistema_EMAs"]["score_numerico"]
        padroes_score_num = indicadores.get("Padroes_Graficos", {}).get("score_numerico", 0)
        
        # Score final: 100% EMAs (padrões descontinuados)
        score_consolidado = emas_score_num
        
        return {
            "bloco": "tecnico",
            "peso_bloco": "40%",
            "score_consolidado": round(score_consolidado, 2),
            "score_consolidado_100": round(score_consolidado * 10, 1),  # ← NOVO: Base 100
            "classificacao_consolidada": interpretar_classificacao(score_consolidado),
            "timestamp": dados_indicadores["timestamp"],
            "metodo": "legacy_compatibilidade",
            "indicadores": {
                "Sistema_EMAs": {
                    "valor": indicadores["Sistema_EMAs"]["valor"],
                    "score": round(emas_score_num, 1),
                    "peso": "30%",
                    "fonte": indicadores["Sistema_EMAs"]["fonte"]
                },
                "Padroes_Graficos": {
                    "valor": indicadores.get("Padroes_Graficos", {}).get("valor", "Descontinuado"),
                    "score": round(padroes_score_num, 1),
                    "peso": "0%",
                    "fonte": indicadores.get("Padroes_Graficos", {}).get("fonte", "Sistema"),
                    "observacao": "Temporariamente zerado"
                }
            },
            "observacoes": {
                "emas_peso_atual": "100% do bloco (30% do total)",
                "bbw_status": "Não implementado neste registro",
                "composicao": "Score = 100% EMAs (legado)"
            },
            "status": "success"
        }
        
    except Exception as e:
        return {
            "bloco": "tecnico",
            "status": "error",
            "erro": f"Erro sistema legado: {str(e)}"
        }

def get_bbw_interpretation(bbw_percentage: float) -> str:
    """Interpretação rápida do BBW"""
    if bbw_percentage < 5:
        return "Compressão extrema - breakout iminente"
    elif bbw_percentage < 10:
        return "Volatilidade baixa - acumulação"
    elif bbw_percentage < 20:
        return "Volatilidade normal"
    elif bbw_percentage < 30:
        return "Volatilidade alta - cautela"
    else:
        return "Volatilidade extrema - evitar posições"

def generate_technical_alerts_bbw(score_final: float, timeframes: dict, bbw_data: dict) -> list:
    """Gera alertas incluindo BBW"""
    alerts = []
    
    try:
        # Alertas score baixo
        if score_final < 4:
            alerts.append(f"🚨 Score técnico crítico: {score_final:.1f}/10 - Sair da posição")
        elif score_final < 6:
            alerts.append(f"⚠️ Score técnico baixo: {score_final:.1f}/10 - Reduzir alavancagem")
        
        # Alertas BBW
        bbw_percentage = bbw_data.get("percentage", 15)
        if bbw_percentage < 5:
            alerts.append(f"🎯 BBW comprimido: {bbw_percentage:.1f}% - Preparar para breakout")
        elif bbw_percentage > 30:
            alerts.append(f"🌪️ BBW extremo: {bbw_percentage:.1f}% - Volatilidade perigosa")
        
        # Divergência componentes
        score_emas = timeframes.get("semanal", {}).get("scores", {}).get("consolidado", 5)
        score_bbw = bbw_data.get("score", 5)
        
        if abs(score_emas - score_bbw) > 4:
            alerts.append("🔄 Conflito EMAs vs BBW - analisar contexto")
        
        return alerts
        
    except Exception as e:
        return [f"⚠️ Erro alertas BBW: {str(e)}"]

def generate_technical_alerts(score_final: float, timeframes: dict) -> list:
    """Gera alertas apenas EMAs (compatibilidade)"""
    alerts = []
    
    try:
        if score_final < 4:
            alerts.append(f"🚨 Score EMAs baixo: {score_final:.1f}/10 - Reduzir alavancagem")
        elif score_final < 6:
            alerts.append(f"⚠️ Score EMAs neutro: {score_final:.1f}/10 - Cautela recomendada")
        
        # Alertas por timeframe
        semanal = timeframes.get("semanal", {})
        diario = timeframes.get("diario", {})
        
        semanal_score = semanal.get("scores", {}).get("consolidado", 10)
        diario_score = diario.get("scores", {}).get("consolidado", 10)
        
        if semanal_score < 6:
            alerts.append("📉 Estrutura semanal enfraquecendo")
        
        if abs(semanal_score - diario_score) > 3:
            alerts.append(f"🔄 Divergência timeframes: {abs(semanal_score - diario_score):.1f}pts")
        
        return alerts
        
    except Exception as e:
        return [f"⚠️ Erro gerando alertas: {str(e)}"]