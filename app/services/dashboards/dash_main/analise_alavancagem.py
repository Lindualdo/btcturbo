# source: app/services/dashboards/dash_main/analise_alavancagem.py

import logging
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)

def executar_analise_alavancagem(alavancagem_permitida) -> dict:
    """
    Camada 3: Análise Alavancagem
    
    Input: Score mercado + indicadores ciclo + RSI mensal
    Output: Limite margem alavancagem (max 3x)
    """
    try:
        #1. dados alavancagem
        logger.info("⚖️ Executando Camada 3: Análise Alavancagem...")
        logger.info(f"⚖️ Alavancagem permitida... {alavancagem_permitida}" )
        
        # 2. Buscar dados posição atual para cálculos financeiros
        dados_posicao = _obter_dados_posicao()
        logger.info(f"⚖️ dados posição obtida" )

        # 3. Calcular simulação financeira 
        simulacao = _calcular_simulacao_financeira(dados_posicao, alavancagem_permitida)
        logger.info(f"⚖️ simulação realizada" )
        # 4. Construir resposta
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "alavancagem_maxima": round(alavancagem_permitida, 1),
            "alavancagem_permitida": round(alavancagem_permitida, 1),
            "alavancagem_atual": dados_posicao.get("alavancagem_atual", 0),
            "posicao_financeira": {
                "divida_total": dados_posicao.get("divida_total", 0),
                "capital_liquido": dados_posicao.get("capital_liquido", 0),
                "posicao_total": dados_posicao.get("posicao_total", 0),
                "valor_disponivel": simulacao.get("valor_disponivel", 0),
                "valor_a_reduzir": simulacao.get("valor_a_reduzir", 0),
                "status_posicao": simulacao.get("status", "indefinido")
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro Camada 3 Alavancagem: {str(e)}")
        return {
            "status": "error",
            "erro": str(e),
            "alavancagem_permitida": 0.0,
            "timestamp": datetime.utcnow().isoformat()
        }

def _obter_dados_posicao() -> dict:
    """Extrai dados financeiros da posição atual"""
    try:
        from app.services.indicadores import riscos
        dados_pos = riscos.obter_indicadores()
        
        if dados_pos.get("status") != "success":
            logger.warning("⚠️ Dados posição indisponíveis")
            return {}
        
        posicao = dados_pos.get("posicao_atual", {})
        
        # Extrair valores numéricos - mapeamento correto V2
        alavancagem_atual = posicao.get("alavancagem_atual", {}).get("valor_numerico", 0)
        divida_total = posicao.get("divida_total", {}).get("valor_numerico", 0)  # total_borrowed
        capital_liquido = posicao.get("capital_liquido", {}).get("valor_numerico", 0)  # net_asset_value
        posicao_total = posicao.get("posicao_total", {}).get("valor_numerico", 0)  # supplied_asset_value
        
        return {
            "alavancagem_atual": float(alavancagem_atual) if alavancagem_atual else 0,
            "divida_total": float(divida_total) if divida_total else 0,
            "capital_liquido": float(capital_liquido) if capital_liquido else 0,
            "posicao_total": float(posicao_total) if posicao_total else 0
        }
        
    except Exception as e:
        logger.error(f"❌ Erro dados posição: {str(e)}")
        return {}

def _calcular_simulacao_financeira(dados_posicao: dict, alavancagem_permitida: float) -> dict:

    try:
        capital_liquido = dados_posicao.get("capital_liquido", 0)
        posicao_atual_total = dados_posicao.get("posicao_total", 0)
        
        if capital_liquido <= 0:
            logger.warning("⚠️ Capital líquido inválido")
            return {"status": "erro", "valor_disponivel": 0, "valor_a_reduzir": 0}
        
        # FÓRMULA V2 EXATA
        posicao_alvo = alavancagem_permitida * capital_liquido
        diferenca = posicao_alvo - posicao_atual_total
        
        logger.info(f"📊 V2 Formula: Alvo=${posicao_alvo:,.0f} - Atual=${posicao_atual_total:,.0f} = ${diferenca:,.0f}")
        
        if diferenca > 0:
            # Pode aumentar alavancagem
            status = "pode_aumentar"
            valor_disponivel = diferenca
            valor_a_reduzir = 0
        elif diferenca < 0:
            # Deve reduzir alavancagem
            status = "deve_reduzir"
            valor_disponivel = 0
            valor_a_reduzir = abs(diferenca)
        else:
            # Exatamente no limite
            status = "adequada"
            valor_disponivel = 0
            valor_a_reduzir = 0
            
        return {
            "status": status,
            "valor_disponivel": valor_disponivel,
            "valor_a_reduzir": valor_a_reduzir
        }
            
    except Exception as e:
        logger.error(f"❌ Erro simulação financeira: {str(e)}")
        return {"status": "erro", "valor_disponivel": 0, "valor_a_reduzir": 0}