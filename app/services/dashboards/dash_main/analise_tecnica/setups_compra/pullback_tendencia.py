# app/services/dashboards/dash_main/analise_tecnica/setups_compra/pullback_tendencia.py

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def detectar_pullback_tendencia(dados_tecnicos: Dict[str, Any]) -> Dict[str, Any]:
    """
    Setup PULLBACK TENDÊNCIA - RSI < 45 + EMA144 ±3%
    
    Args:
        dados_tecnicos: Dados técnicos consolidados
    
    Returns:
        Dict com resultado da detecção
    """
    try:
        logger.info("🔍 Detectando Pullback Tendência...")
        
        # Extrair dados
        rsi = dados_tecnicos.get('rsi_4h', 0)
        ema_distance = dados_tecnicos.get('distancias', {}).get('ema_144_distance', 0)
        
        # Condições do setup
        condicao_rsi = rsi < 45
        condicao_ema = -3 <= ema_distance <= 3
        
        logger.info(f"🔍 RSI {rsi} < 45: {condicao_rsi}")
        logger.info(f"🔍 EMA144 dist {ema_distance:+.1f}% ±3%: {condicao_ema}")
        
        if condicao_rsi and condicao_ema:
            logger.info("✅ PULLBACK TENDÊNCIA identificado!")
            
            # Calcular força baseada na proximidade das condições
            forca = _calcular_forca_pullback(rsi, ema_distance)
            urgencia = _definir_urgencia_pullback(forca)
            
            return {
                "encontrado": True,
                "setup": "PULLBACK_TENDENCIA",
                "forca": forca,
                "tamanho_posicao": 30,  # Mockado v1.5.4
                "dados_tecnicos": dados_tecnicos,
                "estrategia": {
                    "decisao": "COMPRAR",
                    "setup": "PULLBACK_TENDENCIA",
                    "urgencia": urgencia,
                    "justificativa": f"Pullback tendência: RSI {rsi} + EMA144 dist {ema_distance:+.1f}%"
                }
            }
        else:
            logger.info("❌ Pullback Tendência não identificado")
            return {
                "encontrado": False,
                "setup": "PULLBACK_TENDENCIA",
                "dados_tecnicos": dados_tecnicos,
                "detalhes": f"Condições não atendidas: RSI={rsi}, EMA_dist={ema_distance:+.1f}%"
            }
            
    except Exception as e:
        logger.error(f"❌ Erro detectar pullback: {str(e)}")
        return {
            "encontrado": False,
            "setup": "PULLBACK_TENDENCIA",
            "erro": str(e),
            "dados_tecnicos": dados_tecnicos
        }

def _calcular_forca_pullback(rsi: float, ema_distance: float) -> str:
    """Calcula força baseada na proximidade das condições ideais"""
    if rsi < 35 and abs(ema_distance) < 1:
        return "muito_alta"
    elif rsi < 40 and abs(ema_distance) < 2:
        return "alta"
    elif rsi < 45 and abs(ema_distance) < 3:
        return "media"
    else:
        return "baixa"

def _definir_urgencia_pullback(forca: str) -> str:
    """Define urgência baseada na força do setup"""
    urgencia_map = {
        "muito_alta": "critica",
        "alta": "alta", 
        "media": "media",
        "baixa": "baixa"
    }
    return urgencia_map.get(forca, "baixa")