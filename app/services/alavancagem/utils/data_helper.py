# app/services/alavancagem/utils/data_helper.py

import logging
from typing import Optional, Dict
from app.services.utils.helpers.postgres.base import execute_query

logger = logging.getLogger(__name__)

def get_alavancagem_permitida() -> Optional[float]:
    """
    Busca nível de alavancagem da última decisão estratégica
    
    Returns:
        float: Nível de alavancagem permitida ou None se não encontrar
    """
    try:
        logger.info("🔍 Buscando alavancagem da última decisão estratégica...")
        
        query = """
            SELECT alavancagem
            FROM decisao_estrategica 
            ORDER BY timestamp DESC 
            LIMIT 1
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            alavancagem = float(result['alavancagem'])
            logger.info(f"✅ Alavancagem permitida encontrada: {alavancagem}x")
            return alavancagem
        else:
            logger.warning("⚠️ Nenhuma decisão estratégica encontrada")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar alavancagem permitida: {str(e)}")
        return None

def obter_dados_posicao() -> dict:
    """CÓPIA EXATA da função _obter_dados_posicao do dash-main"""
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

def calcular_simulacao_financeira(dados_posicao: dict, alavancagem_permitida: float) -> dict:
    """CÓPIA EXATA da função _calcular_simulacao_financeira do dash-main"""
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