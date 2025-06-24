# app/services/dashboards/dash_main/analise_tecnica/setups_compra/cruzamento_medias.py

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def detectar_cruzamento_medias(dados_tecnicos: Dict[str, Any]) -> Dict[str, Any]:
    """
    Setup CRUZAMENTO MÉDIAS - EMA17 > EMA144 com distância significativa
    
    Args:
        dados_tecnicos: Dados técnicos consolidados
    
    Returns:
        Dict com resultado da detecção
    """
    try:
        logger.info("🔍 Detectando Cruzamento Médias...")
        
        # Extrair dados
        precos = dados_tecnicos.get('precos', {})
        ema_17 = precos.get('ema_17', 0)
        ema_144 = precos.get('ema_144', 0)
        
        # TODO: Implementar lógica real de cruzamento
        # - Verificar EMA17 > EMA144
        # - Calcular distância entre médias
        # - Validar tendência de alta
        # - Confirmar momentum
        
        # MOCKADO v1.5.4 - simulando não encontrado para foco em outros setups
        encontrado = False
        
        if ema_17 > 0 and ema_144 > 0:
            distancia_emas = ((ema_17 - ema_144) / ema_144) * 100
            logger.info(f"🔍 EMA17 vs EMA144: dist {distancia_emas:+.2f}%")
            
            # Condição mockada (não ativa)
            condicao_cruzamento = False  # ema_17 > ema_144 and distancia_emas > 0.5
            
            if condicao_cruzamento:
                logger.info("✅ CRUZAMENTO MÉDIAS identificado!")
                
                return {
                    "encontrado": True,
                    "setup": "CRUZAMENTO_MEDIAS",
                    "forca": "media",
                    "tamanho_posicao": 25,  # Mockado v1.5.4
                    "dados_tecnicos": dados_tecnicos,
                    "estrategia": {
                        "decisao": "COMPRAR",
                        "setup": "CRUZAMENTO_MEDIAS",
                        "urgencia": "media",
                        "justificativa": f"Cruzamento médias: EMA17 > EMA144 ({distancia_emas:+.2f}%)"
                    }
                }
        
        logger.info("❌ Cruzamento Médias não identificado")
        return {
            "encontrado": False,
            "setup": "CRUZAMENTO_MEDIAS",
            "dados_tecnicos": dados_tecnicos,
            "detalhes": "Cruzamento não confirmado (mockado v1.5.4)"
        }
            
    except Exception as e:
        logger.error(f"❌ Erro detectar cruzamento: {str(e)}")
        return {
            "encontrado": False,
            "setup": "CRUZAMENTO_MEDIAS",
            "erro": str(e),
            "dados_tecnicos": dados_tecnicos
        }

def _calcular_forca_cruzamento(distancia_emas: float) -> str:
    """Calcula força baseada na distância entre EMAs"""
    if distancia_emas > 2.0:
        return "muito_alta"
    elif distancia_emas > 1.0:
        return "alta"
    elif distancia_emas > 0.5:
        return "media"
    else:
        return "baixa"