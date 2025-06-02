# app/services/scores/tecnico.py

from app.services.indicadores import tecnico as indicadores_tecnico

def calcular_emas_score(score_numerico):
    """Score já vem calculado do sistema EMAs - usar direto"""
    return score_numerico

def calcular_padroes_score(score_numerico):
    """Score já vem calculado dos padrões gráficos - usar direto"""
    return score_numerico

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
    """Calcula score consolidado do bloco TÉCNICO usando EMAs reais"""
    # 1. Obter dados brutos da API
    dados_indicadores = indicadores_tecnico.obter_indicadores()
    
    if dados_indicadores.get("status") != "success":
        return {
            "bloco": "tecnico",
            "status": "error",
            "erro": "Dados não disponíveis"
        }
    
    indicadores = dados_indicadores["indicadores"]
    
    # 2. Verificar se temos dados EMAs detalhados ou legados
    if "Score_Final_Ponderado" in indicadores:
        # Novo sistema com EMAs detalhadas
        return calcular_score_emas_detalhadas(dados_indicadores)
    else:
        # Sistema legado
        return calcular_score_legado(dados_indicadores)

def calcular_score_emas_detalhadas(dados_indicadores):
    """Calcula score usando EMAs detalhadas por timeframe"""
    try:
        indicadores = dados_indicadores["indicadores"]
        timeframes = dados_indicadores.get("timeframes", {})
        
        # Score final já calculado e ponderado (70% semanal + 30% diário)
        score_final = indicadores["Score_Final_Ponderado"]["score_numerico"]
        
        # Extrair scores individuais para detalhamento
        semanal = timeframes.get("semanal", {})
        diario = timeframes.get("diario", {})
        
        return {
            "bloco": "tecnico",
            "peso_bloco": "20%",
            "score_consolidado": round(score_final, 2),
            "classificacao_consolidada": interpretar_classificacao(score_final),
            "timestamp": dados_indicadores["timestamp"],
            "metodo": "emas_multitimeframe",
            "timeframes": {
                "semanal": {
                    "peso": "70%",
                    "score_total": semanal.get("scores", {}).get("consolidado", 0),
                    "alinhamento": semanal.get("scores", {}).get("alinhamento", 0),
                    "posicao": semanal.get("scores", {}).get("posicao", 0),
                    "emas": semanal.get("emas", {})
                },
                "diario": {
                    "peso": "30%", 
                    "score_total": diario.get("scores", {}).get("consolidado", 0),
                    "alinhamento": diario.get("scores", {}).get("alinhamento", 0),
                    "posicao": diario.get("scores", {}).get("posicao", 0),
                    "emas": diario.get("emas", {})
                }
            },
            "indicadores": {
                "Sistema_EMAs_Multitimeframe": {
                    "valor": indicadores["Score_Final_Ponderado"]["valor"],
                    "score": round(score_final, 1),
                    "classificacao": interpretar_classificacao(score_final),
                    "peso": "20%",
                    "fonte": indicadores["Score_Final_Ponderado"]["fonte"],
                    "ponderacao": "70% semanal + 30% diário"
                },
                "Padroes_Graficos": {
                    "valor": "Descontinuado",
                    "score": 0.0,
                    "classificacao": "N/A",
                    "peso": "0%",
                    "fonte": indicadores.get("Padroes_Graficos", {}).get("fonte", "Sistema"),
                    "observacao": "Peso zerado - foco em EMAs"
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
    """Calcula score usando sistema legado (compatibilidade)"""
    try:
        indicadores = dados_indicadores["indicadores"]
        
        # Extrair scores já calculados
        emas_score_num = indicadores["Sistema_EMAs"]["score_numerico"]
        padroes_score_num = indicadores["Padroes_Graficos"]["score_numerico"]
        
        emas_score = calcular_emas_score(emas_score_num)
        padroes_score = calcular_padroes_score(padroes_score_num)
        
        # Aplicar pesos: EMAs: 20% do total, Padrões: 0% (descontinuado)
        score_consolidado = (emas_score * 1.0) + (padroes_score * 0.0)
        
        return {
            "bloco": "tecnico",
            "peso_bloco": "20%",
            "score_consolidado": round(score_consolidado, 2),
            "classificacao_consolidada": interpretar_classificacao(score_consolidado),
            "timestamp": dados_indicadores["timestamp"],
            "metodo": "legacy_compatibilidade",
            "indicadores": {
                "Sistema_EMAs": {
                    "valor": indicadores["Sistema_EMAs"]["valor"],
                    "score": round(emas_score, 1),
                    "peso": "20%",
                    "fonte": indicadores["Sistema_EMAs"]["fonte"]
                },
                "Padroes_Graficos": {
                    "valor": indicadores["Padroes_Graficos"]["valor"],
                    "score": round(padroes_score, 1),
                    "peso": "0%",
                    "fonte": indicadores["Padroes_Graficos"]["fonte"],
                    "observacao": "Temporariamente zerado"
                }
            },
            "observacoes": {
                "emas_peso_atual": "100% do bloco (20% do total)",
                "padroes_status": "Zerado - aguardando reimplementação",
                "composicao": "Score = 100% EMAs + 0% Padrões"
            },
            "status": "success"
        }
        
    except Exception as e:
        return {
            "bloco": "tecnico",
            "status": "error",
            "erro": f"Erro sistema legado: {str(e)}"
        }

def generate_technical_alerts(score_final: float, timeframes: dict) -> list:
    """Gera alertas baseados nos scores técnicos"""
    alerts = []
    
    try:
        # Alertas de score baixo
        if score_final < 4:
            alerts.append(f"🚨 Score técnico baixo: {score_final:.1f}/10 - Reduzir alavancagem")
        elif score_final < 6:
            alerts.append(f"⚠️ Score técnico neutro: {score_final:.1f}/10 - Cautela recomendada")
        
        # Alertas por timeframe
        semanal = timeframes.get("semanal", {})
        diario = timeframes.get("diario", {})
        
        semanal_score = semanal.get("scores", {}).get("consolidado", 10)
        diario_score = diario.get("scores", {}).get("consolidado", 10)
        
        if semanal_score < 6:
            alerts.append("📉 Estrutura semanal enfraquecendo - tendência macro em risco")
        
        if diario_score < 4:
            alerts.append("📊 Momentum diário negativo - aguardar reversão")
        
        # Divergência entre timeframes
        divergence = abs(semanal_score - diario_score)
        if divergence > 3:
            alerts.append(f"🔄 Divergência entre timeframes: {divergence:.1f} pontos")
        
        # Alinhamento quebrado
        semanal_alignment = semanal.get("scores", {}).get("alinhamento", 10)
        if semanal_alignment < 6:
            alerts.append("💔 Alinhamento EMAs semanal quebrado")
        
        return alerts
        
    except Exception as e:
        return [f"⚠️ Erro gerando alertas: {str(e)}"]