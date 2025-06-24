# app/services/dashboards/dash_main/analise_tecnica/setups_compra/teste_suporte.py

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def detectar_teste_suporte(dados_tecnicos: Dict[str, Any]) -> Dict[str, Any]:
    """
    Setup TESTE SUPORTE - Preço próximo EMA144 ±2%
    
    Args:
        dados_tecnicos: Dados técnicos consolidados
    
    Returns:
        Dict com resultado da detecção
    """
    try:
        logger.info("🔍 Detectando Teste Suporte...")
        
        # Extrair dados
        ema_distance = dados_tecnicos.get('distancias', {}).get('ema_144_distance', 0)
        preco_atual = dados_tecnicos.get('precos', {}).get('atual', 0)
        
        # Condição do setup - preço próximo da EMA144
        condicao_suporte = -2 <= ema_distance <= 2
        
        logger.info(f"🔍 EMA144 dist {ema_distance:+.1f}% ±2%: {condicao_suporte}")
        
        if condicao_suporte:
            logger.info("✅ TESTE SUPORTE identificado!")
            
            # Calcular força baseada na proximidade do suporte
            forca = _calcular_forca_suporte(ema_distance)
            
            return {
                "encontrado": True,
                "setup": "TESTE_SUPORTE",
                "forca": forca,
                "tamanho_posicao": 25,  # Mockado v1.5.4
                "dados_tecnicos": dados_tecnicos,
                "estrategia": {
                    "decisao": "COMPRAR",
                    "setup": "TESTE_SUPORTE",
                    "urgencia": "media",
                    "justificativa": f"Teste suporte EMA144: preço dist {ema_distance:+.1f}%"
                }
            }
        else:
            logger.info("❌ Teste Suporte não identificado")
            return {
                "encontrado": False,
                "setup": "TESTE_SUPORTE",
                "dados_tecnicos": dados_tecnicos,
                "detalhes": f"EMA144 dist {ema_distance:+.1f}% fora da faixa ±2%"
            }
            
    except Exception as e:
        logger.error(f"❌ Erro detectar teste suporte: {str(e)}")
        return {
            "encontrado": False,
            "setup": "TESTE_SUPORTE",
            "erro": str(e),
            "dados_tecnicos": dados_tecnicos
        }

def _calcular_forca_suporte(ema_distance: float) -> str:
    """Calcula força baseada na proximidade da EMA144"""
    abs_distance = abs(ema_distance)
    
    if abs_distance < 0.5:
        return "muito_alta"
    elif abs_distance < 1.0:
        return "alta"
    elif abs_distance < 1.5:
        return "media"
    elif abs_distance < 2.0:
        return "baixa"
    else:
        return "nenhuma"