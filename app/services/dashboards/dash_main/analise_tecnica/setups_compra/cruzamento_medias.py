# app/services/dashboards/dash_main/analise_tecnica/setups_compra/cruzamento_medias.py

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def detectar_cruzamento_medias(dados_tecnicos: Dict[str, Any]) -> Dict[str, Any]:
    """
    Setup CRUZAMENTO MÉDIAS - EMA17 cruza EMA34 para cima (dados reais TradingView)
    
    Args:
        dados_tecnicos: Dados técnicos consolidados
    
    Returns:
        Dict com resultado da detecção
    """
    try:
        logger.info("🔍 Detectando Cruzamento Médias (EMAs reais 4H)...")
        
        # Extrair dados EMAs reais
        emas_data = dados_tecnicos.get('emas_cruzamento', {})
        ema_17_atual = emas_data.get('ema_17_atual', 0)
        ema_34_atual = emas_data.get('ema_34_atual', 0)
        ema_17_anterior = emas_data.get('ema_17_anterior', 0)
        ema_34_anterior = emas_data.get('ema_34_anterior', 0)
        
        # Validar se dados são reais
        if any(v <= 0 for v in [ema_17_atual, ema_34_atual, ema_17_anterior, ema_34_anterior]):
            raise ValueError("EMAs não disponíveis nos dados técnicos")
        
        logger.info(f"📊 EMA17: atual={ema_17_atual:.2f}, anterior={ema_17_anterior:.2f}")
        logger.info(f"📊 EMA34: atual={ema_34_atual:.2f}, anterior={ema_34_anterior:.2f}")
        
        # CONDIÇÃO: EMA17 cruza EMA34 de baixo para cima
        cruzamento_ocorreu = (ema_17_atual > ema_34_atual) and (ema_17_anterior <= ema_34_anterior)
        
        logger.info(f"🔍 EMA17 > EMA34 atual: {ema_17_atual > ema_34_atual}")
        logger.info(f"🔍 EMA17 <= EMA34 anterior: {ema_17_anterior <= ema_34_anterior}")
        logger.info(f"🔍 Cruzamento detectado: {cruzamento_ocorreu}")
        
        if cruzamento_ocorreu:
            logger.info("✅ CRUZAMENTO MÉDIAS identificado com EMAs reais!")
            
            # Calcular força baseada na diferença entre EMAs
            forca = _calcular_forca_cruzamento(ema_17_atual, ema_34_atual)
            
            return {
                "encontrado": True,
                "setup": "CRUZAMENTO_MEDIAS",
                "forca": forca,
                "tamanho_posicao": 25,  # Mockado v1.5.4
                "dados_tecnicos": dados_tecnicos,
                "estrategia": {
                    "decisao": "COMPRAR",
                    "setup": "CRUZAMENTO_MEDIAS",
                    "urgencia": "alta" if forca == "muito_alta" else "media",
                    "justificativa": f"Cruzamento médias: EMA17 ${ema_17_atual:.0f} x EMA34 ${ema_34_atual:.0f}"
                }
            }
        else:
            logger.info("❌ Cruzamento Médias não identificado")
            return {
                "encontrado": False,
                "setup": "CRUZAMENTO_MEDIAS",
                "dados_tecnicos": dados_tecnicos,
                "detalhes": f"Cruzamento não ocorreu: EMA17 atual > EMA34 atual ({ema_17_atual > ema_34_atual}), EMA17 anterior <= EMA34 anterior ({ema_17_anterior <= ema_34_anterior})"
            }
            
    except Exception as e:
        logger.error(f"❌ Erro detectar cruzamento: {str(e)}")
        return {
            "encontrado": False,
            "setup": "CRUZAMENTO_MEDIAS",
            "erro": str(e),
            "dados_tecnicos": dados_tecnicos
        }

def _calcular_forca_cruzamento(ema_17: float, ema_34: float) -> str:
    """Calcula força baseada na diferença percentual entre EMAs após cruzamento"""
    # Diferença percentual: quanto EMA17 está acima da EMA34
    diferenca_percent = ((ema_17 - ema_34) / ema_34) * 100
    
    # Quanto maior a diferença após cruzamento, mais forte o sinal
    if diferenca_percent > 1.0:
        return "muito_alta"
    elif diferenca_percent > 0.5:
        return "alta"
    elif diferenca_percent > 0.1:
        return "media"
    else:
        return "baixa"