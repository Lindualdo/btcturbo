# app/services/alavancagem/alavancagem_service.py

import logging
from datetime import datetime
from typing import Dict
from .utils.data_helper import (
    get_alavancagem_permitida,
    get_dados_posicao_financeira,
    calcular_simulacao_alavancagem
)

logger = logging.getLogger(__name__)

def calcular_alavancagem() -> Dict:
    """
    API principal para cálculo de alavancagem
    
    Aplica as mesmas regras do dash-main, mas busca alavancagem 
    permitida da tabela decisao_estrategica (último registro)
    
    Returns:
        Dict com dados de alavancagem no formato especificado
    """
    try:
        logger.info("⚖️ Iniciando cálculo de alavancagem...")
        
        # 1. Buscar alavancagem permitida da decisão estratégica
        alavancagem_permitida = get_alavancagem_permitida()
        if alavancagem_permitida is None:
            return _erro_response("Alavancagem permitida não encontrada")
        
        # 2. Obter dados da posição financeira atual
        dados_posicao = get_dados_posicao_financeira()
        if dados_posicao is None:
            return _erro_response("Dados da posição financeira não encontrados")
        
        # 3. Calcular simulação de alavancagem
        simulacao = calcular_simulacao_alavancagem(dados_posicao, alavancagem_permitida)
        
        # 4. Construir resposta no formato especificado
        resposta = {
            "alavancagem": {
                "atual": round(dados_posicao["alavancagem_atual"], 2),
                "status": simulacao["status"],
                "permitida": round(alavancagem_permitida, 1),
                "divida_total": round(dados_posicao["divida_total"], 6),
                "valor_a_reduzir": round(simulacao["valor_a_reduzir"], 0),
                "valor_disponivel": round(simulacao["valor_disponivel"], 8)
            }
        }
        
        logger.info(f"✅ Alavancagem calculada: {resposta['alavancagem']['atual']:.2f}x → {resposta['alavancagem']['permitida']:.1f}x ({resposta['alavancagem']['status']})")
        
        return resposta
        
    except Exception as e:
        logger.error(f"❌ Erro no cálculo de alavancagem: {str(e)}")
        return _erro_response(f"Erro interno: {str(e)}")

def _erro_response(mensagem: str) -> Dict:
    """
    Cria resposta de erro padronizada
    
    Args:
        mensagem: Mensagem de erro
        
    Returns:
        Dict com erro e estrutura vazia
    """
    logger.error(f"❌ {mensagem}")
    
    return {
        "erro": mensagem,
        "timestamp": datetime.utcnow().isoformat(),
        "alavancagem": {
            "atual": 0.0,
            "status": "erro",
            "permitida": 0.0,
            "divida_total": 0.0,
            "valor_a_reduzir": 0.0,
            "valor_disponivel": 0.0
        }
    }

def get_status_alavancagem() -> Dict:
    """
    Retorna apenas o status atual da alavancagem (versão resumida)
    
    Returns:
        Dict com status simplificado
    """
    try:
        resultado = calcular_alavancagem()
        
        if "erro" in resultado:
            return {
                "status": "erro",
                "erro": resultado["erro"]
            }
        
        alavancagem_data = resultado["alavancagem"]
        
        return {
            "status": "success",
            "alavancagem_atual": alavancagem_data["atual"],
            "alavancagem_permitida": alavancagem_data["permitida"],
            "pode_aumentar": alavancagem_data["status"] == "pode_aumentar",
            "deve_reduzir": alavancagem_data["status"] == "deve_reduzir"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro status alavancagem: {str(e)}")
        return {
            "status": "erro",
            "erro": str(e)
        }