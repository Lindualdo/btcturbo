# app/services/dashboards/dash_main/analise_tecnica/setups_compra/oversold_extremo.py

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def detectar_oversold_extremo(dados_tecnicos: Dict[str, Any]) -> Dict[str, Any]:
    """
    Setup OVERSOLD EXTREMO - RSI < 30
    
    Args:
        dados_tecnicos: Dados técnicos consolidados
    
    Returns:
        Dict com resultado da detecção
    """
    try:
        logger.info("🔍 Detectando Oversold Extremo...")
        
        # Extrair dados
        rsi = dados_tecnicos.get('rsi_4h', 0)
        
        # Condição do setup
        condicao_oversold = rsi < 30
        
        logger.info(f"🔍 RSI {rsi} < 30: {condicao_oversold}")
        
        if condicao_oversold:
            logger.info("✅ OVERSOLD EXTREMO identificado!")
            
            # Calcular força baseada na intensidade do oversold
            forca = _calcular_forca_oversold(rsi)
            
            return {
                "encontrado": True,
                "setup": "OVERSOLD_EXTREMO",
                "forca": forca,
                "tamanho_posicao": 40,  # Mockado v1.5.4
                "dados_tecnicos": dados_tecnicos,
                "estrategia": {
                    "decisao": "COMPRAR",
                    "setup": "OVERSOLD_EXTREMO",
                    "urgencia": "critica",
                    "justificativa": f"Oversold extremo: RSI {rsi} < 30"
                }
            }
        else:
            logger.info("❌ Oversold Extremo não identificado")
            return {
                "encontrado": False,
                "setup": "OVERSOLD_EXTREMO",
                "dados_tecnicos": dados_tecnicos,
                "detalhes": f"RSI {rsi} >= 30"
            }
            
    except Exception as e:
        logger.error(f"❌ Erro detectar oversold: {str(e)}")
        return {
            "encontrado": False,
            "setup": "OVERSOLD_EXTREMO",
            "erro": str(e),
            "dados_tecnicos": dados_tecnicos
        }

def _calcular_forca_oversold(rsi: float) -> str:
    """Calcula força baseada na intensidade do oversold"""
    if rsi < 15:
        return "muito_alta"
    elif rsi < 20:
        return "alta"
    elif rsi < 25:
        return "media"
    elif rsi < 30:
        return "baixa"
    else:
        return "nenhuma"