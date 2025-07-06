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

def get_dados_posicao_financeira() -> Optional[Dict]:
    """
    Busca dados financeiros atuais da posição
    
    Returns:
        Dict com dados da posição ou None
    """
    try:
        logger.info("💰 Obtendo dados posição financeira...")
        
        # Buscar dados do bloco riscos (health factor, dívida, etc)
        from app.services.indicadores import riscos
        dados_riscos = riscos.obter_indicadores()
        
        if not dados_riscos or 'aave' not in dados_riscos:
            logger.warning("⚠️ Dados AAVE não encontrados")
            return None
            
        aave_data = dados_riscos['aave']
        
        # Extrair dados financeiros
        divida_total = aave_data.get('totalBorrowsUSD', 0)
        collateral_total = aave_data.get('totalCollateralUSD', 0)
        capital_liquido = collateral_total - divida_total
        
        # Calcular alavancagem atual
        alavancagem_atual = divida_total / capital_liquido if capital_liquido > 0 else 0
        
        dados_posicao = {
            "divida_total": divida_total,
            "collateral_total": collateral_total,
            "capital_liquido": capital_liquido,
            "alavancagem_atual": alavancagem_atual,
            "health_factor": aave_data.get('healthFactor', 0),
            "valor_disponivel": aave_data.get('availableBorrowsUSD', 0)
        }
        
        logger.info(f"✅ Posição: Capital ${capital_liquido:,.0f} | Alavancagem {alavancagem_atual:.2f}x")
        return dados_posicao
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter dados posição: {str(e)}")
        return None

def calcular_simulacao_alavancagem(dados_posicao: Dict, alavancagem_permitida: float) -> Dict:
    """
    Calcula simulação financeira para alavancagem permitida
    
    Args:
        dados_posicao: Dados financeiros atuais
        alavancagem_permitida: Nível de alavancagem permitido
        
    Returns:
        Dict com resultado da simulação
    """
    try:
        capital_liquido = dados_posicao.get("capital_liquido", 0)
        alavancagem_atual = dados_posicao.get("alavancagem_atual", 0)
        valor_disponivel = dados_posicao.get("valor_disponivel", 0)
        
        # Calcular valores para alavancagem permitida
        divida_maxima = capital_liquido * alavancagem_permitida
        divida_atual = dados_posicao.get("divida_total", 0)
        
        # Determinar se pode aumentar ou deve reduzir
        diferenca = divida_maxima - divida_atual
        
        if diferenca > 0:
            # Pode aumentar alavancagem
            status = "pode_aumentar"
            valor_disponivel_real = min(diferenca, valor_disponivel)
            valor_a_reduzir = 0
        else:
            # Deve reduzir alavancagem
            status = "deve_reduzir"
            valor_disponivel_real = 0
            valor_a_reduzir = abs(diferenca)
        
        return {
            "status": status,
            "valor_disponivel": valor_disponivel_real,
            "valor_a_reduzir": valor_a_reduzir,
            "divida_maxima": divida_maxima,
            "diferenca": diferenca
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na simulação: {str(e)}")
        return {
            "status": "erro",
            "valor_disponivel": 0,
            "valor_a_reduzir": 0,
            "divida_maxima": 0,
            "diferenca": 0
        }