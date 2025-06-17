# services/v3/utils/analise/tatica/setup_hunter.py
import logging
from datetime import datetime
from .setup_matriz import aplicar_matriz_decisao

logger = logging.getLogger(__name__)

def executar_analise_tatica(mercado_data: dict, risco_data: dict, alavancagem_data: dict) -> dict:
    """
    Análise Tática - Camada 4 (Execução)
    Setup + Estratégia final baseada nas 3 camadas anteriores
    """
    try:
        logger.info("🎯 Executando análise tática...")
        
        # 1. Detectar setup 4H baseado em RSI + EMA144
        setup_detectado = _detectar_setup_4h(mercado_data)
        
        # 2. Aplicar matriz de decisão Ciclo × Setup
        decisao_matriz = aplicar_matriz_decisao(
            ciclo=mercado_data["ciclo"],
            setup=setup_detectado["setup"],
            mercado_data=mercado_data,
            risco_data=risco_data,
            alavancagem_data=alavancagem_data
        )
        
        # 3. Determinar urgência baseada no contexto
        urgencia = _determinar_urgencia(setup_detectado, decisao_matriz, risco_data)
        
        # 4. Gerar justificativa completa
        justificativa = _gerar_justificativa_tatica(
            setup_detectado, decisao_matriz, mercado_data, urgencia
        )
        
        resultado = {
            "decisao": decisao_matriz["decisao"],
            "setup": setup_detectado["setup"],
            "tamanho_percent": decisao_matriz["tamanho_percent"],
            "urgencia": urgencia,
            "justificativa": justificativa,
            
            # Detalhamento do setup
            "setup_detalhes": {
                "rsi_4h": setup_detectado["rsi_4h"],
                "ema_distance": setup_detectado["ema_distance"],
                "condicao_principal": setup_detectado["condicao"],
                "forca_setup": setup_detectado["forca"]
            },
            
            # Contexto da decisão
            "contexto_decisao": {
                "ciclo_base": mercado_data["ciclo"],
                "score_mercado": mercado_data["score"],
                "health_factor_ok": risco_data["health_factor"] > 1.2,
                "alavancagem_disponivel": alavancagem_data["pode_aumentar"]
            },
            
            # Metadados
            "timestamp": datetime.utcnow().isoformat(),
            "fonte": "setup_hunter + matriz_decisao",
            "status": "success"
        }
        
        logger.info(f"✅ Tática: {decisao_matriz['decisao']} {decisao_matriz['tamanho_percent']}% - Setup {setup_detectado['setup']}")
        return resultado
        
    except Exception as e:
        logger.error(f"❌ Erro análise tática: {str(e)}")
        # Retornar decisão conservadora em caso de erro
        return {
            "decisao": "HOLD",
            "setup": "INDEFINIDO",
            "tamanho_percent": 0,
            "urgencia": "baixa",
            "justificativa": f"Erro na análise tática: {str(e)}. Recomendado aguardar.",
            "setup_detalhes": {},
            "contexto_decisao": {},
            "timestamp": datetime.utcnow().isoformat(),
            "fonte": "erro_sistema",
            "status": "error",
            "erro": str(e)
        }

def _detectar_setup_4h(mercado_data: dict) -> dict:
    """
    Detecta setup 4H baseado em RSI + EMA144 (conforme documentação V2)
    """
    try:
        # Dados técnicos necessários
        rsi_diario = mercado_data["rsi_diario"]  # Proxy para 4H
        ema_distance = mercado_data["ema_distance"]
        
        # Lógica de detecção (da documentação V2)
        if rsi_diario < 30:
            setup = "OVERSOLD_EXTREMO"
            condicao = f"RSI {rsi_diario} < 30"
            forca = "MAXIMA"
            
        elif rsi_diario < 45 and abs(ema_distance) <= 3:
            setup = "PULLBACK_TENDENCIA"
            condicao = f"RSI {rsi_diario} < 45 + EMA±3%"
            forca = "ALTA"
            
        elif abs(ema_distance) <= 1 and 30 <= rsi_diario <= 60:
            setup = "TESTE_SUPORTE"
            condicao = f"Distance ~0% + RSI {rsi_diario}"
            forca = "MEDIA"
            
        elif ema_distance > 5 and 45 <= rsi_diario <= 65:
            setup = "ROMPIMENTO"
            condicao = f"Distance {ema_distance}% > 5% + RSI {rsi_diario}"
            forca = "MEDIA"
            
        elif rsi_diario > 70 and ema_distance > 10:
            setup = "RESISTENCIA"
            condicao = f"RSI {rsi_diario} > 70 + Distance {ema_distance}%"
            forca = "BAIXA"
            
        else:
            setup = "NEUTRO"
            condicao = "Condições não atendem critérios específicos"
            forca = "BAIXA"
        
        return {
            "setup": setup,
            "rsi_4h": rsi_diario,  # Usando RSI diário como proxy
            "ema_distance": ema_distance,
            "condicao": condicao,
            "forca": forca
        }
        
    except Exception as e:
        logger.error(f"❌ Erro detectar setup: {str(e)}")
        return {
            "setup": "ERRO",
            "rsi_4h": 50.0,
            "ema_distance": 0.0,
            "condicao": f"Erro: {str(e)}",
            "forca": "BAIXA"
        }

def _determinar_urgencia(setup_data: dict, decisao_data: dict, risco_data: dict) -> str:
    """
    Determina urgência baseada no setup e contexto de risco
    """
    # Urgência crítica: problemas de risco
    if risco_data["health_factor"] < 1.2:
        return "critica"
    
    # Urgência alta: setups extremos
    if setup_data["forca"] == "MAXIMA":
        return "alta"
    
    # Urgência alta: decisões de redução
    if decisao_data["decisao"] in ["REALIZAR", "REDUZIR"]:
        return "alta"
    
    # Urgência média: setups bons
    if setup_data["forca"] == "ALTA":
        return "media"
    
    # Urgência baixa: resto
    return "baixa"

def _gerar_justificativa_tatica(setup_data: dict, decisao_data: dict, mercado_data: dict, urgencia: str) -> str:
    """
    Gera justificativa completa da decisão tática
    """
    justificativas = []
    
    # Contexto do ciclo
    justificativas.append(f"Ciclo {mercado_data['ciclo']}")
    
    # Setup detectado
    if setup_data["setup"] != "NEUTRO":
        justificativas.append(f"setup {setup_data['setup']} detectado")
    
    # Decisão e tamanho
    if decisao_data["tamanho_percent"] > 0:
        justificativas.append(f"{decisao_data['decisao']} {decisao_data['tamanho_percent']}%")
    else:
        justificativas.append(decisao_data["decisao"])
    
    # Urgência se relevante
    if urgencia in ["critica", "alta"]:
        justificativas.append(f"urgência {urgencia}")
    
    # Condição técnica
    justificativas.append(f"Condição: {setup_data['condicao']}")
    
    return ". ".join(justificativas).capitalize() + "."