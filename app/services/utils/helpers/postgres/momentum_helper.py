# app/services/utils/helpers/postgres/momentum_helper.py - v5.1.3 COM SOPR

import logging
from datetime import datetime
from typing import Dict, Optional
from .base import execute_query

logger = logging.getLogger(__name__)

def get_dados_momentum() -> Optional[Dict]:
    """Busca dados mais recentes do bloco momentum - v5.1.3 COM SOPR"""
    try:
        logger.info("🔍 Buscando dados do bloco MOMENTUM v5.1.3...")
        
        # QUERY ATUALIZADA v5.1.3 - incluindo SOPR
        query = """
            SELECT id, rsi_semanal, funding_rates, exchange_netflow, long_short_ratio,
                   sopr, timestamp, fonte, metadados
            FROM indicadores_momentum 
            ORDER BY id DESC 
            LIMIT 1
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            # LOG DETALHADO para v5.1.3
            logger.info(f"✅ Dados momentum v5.1.3 encontrados:")
            logger.info(f"    ID: {result.get('id')}")
            logger.info(f"    RSI: {result.get('rsi_semanal')}")
            logger.info(f"    Funding: {result.get('funding_rates')}")
            logger.info(f"    Exchange Netflow: {result.get('exchange_netflow')} (compatibilidade)")
            logger.info(f"    SOPR: {result.get('sopr')} ← NOVO v5.1.3")
            logger.info(f"    L/S: {result.get('long_short_ratio')}")
            logger.info(f"    Timestamp: {result.get('timestamp')}")
            
            return result
        else:
            logger.warning("⚠️ Nenhum dado encontrado na tabela indicadores_momentum")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar dados do bloco momentum v5.1.3: {str(e)}")
        return None

def insert_dados_momentum(
    rsi: float, 
    funding: float, 
    netflow: float, 
    ls_ratio: float, 
    sopr: Optional[float] = None,  # ← NOVO v5.1.3
    fonte: str = "Sistema"
) -> bool:
    """
    Insere novos dados no bloco momentum - v5.1.3 COM SOPR
    
    Args:
        rsi: RSI Semanal
        funding: Funding Rates
        netflow: Exchange Netflow (mantido para compatibilidade)
        ls_ratio: Long/Short Ratio
        sopr: SOPR - Spent Output Profit Ratio (NOVO v5.1.3)
        fonte: Fonte dos dados
    
    Returns:
        bool: Sucesso da operação
    """
    try:
        logger.info(f"💾 Inserindo dados momentum v5.1.3:")
        logger.info(f"    RSI={rsi}, Funding={funding}")
        logger.info(f"    Netflow={netflow} (compatibilidade), L/S={ls_ratio}")
        logger.info(f"    SOPR={sopr} ← NOVO v5.1.3")
        
        # QUERY ATUALIZADA v5.1.3 - incluindo SOPR
        query = """
            INSERT INTO indicadores_momentum 
            (rsi_semanal, funding_rates, exchange_netflow, long_short_ratio, sopr, fonte, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (rsi, funding, netflow, ls_ratio, sopr, fonte, datetime.utcnow())
        
        execute_query(query, params)
        logger.info("✅ Dados momentum v5.1.3 inseridos com sucesso (incluindo SOPR)")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dados momentum v5.1.3: {str(e)}")
        return False

def get_historico_momentum(limit: int = 10) -> list:
    """Busca histórico de dados do bloco momentum - v5.1.3 COM SOPR"""
    try:
        logger.info(f"📊 Buscando histórico do bloco MOMENTUM v5.1.3 (últimos {limit} registros)")
        
        # QUERY ATUALIZADA v5.1.3 - incluindo SOPR
        query = """
            SELECT id, rsi_semanal, funding_rates, exchange_netflow, long_short_ratio,
                   sopr, timestamp, fonte
            FROM indicadores_momentum 
            ORDER BY timestamp DESC 
            LIMIT %s
        """
        
        result = execute_query(query, params=(limit,), fetch_all=True)
        
        if result:
            logger.info(f"✅ {len(result)} registros históricos encontrados v5.1.3")
            
            # LOG estatísticas SOPR para debug v5.1.3
            sopr_count = sum(1 for r in result if r.get('sopr') is not None)
            logger.info(f"📈 Registros com SOPR: {sopr_count}/{len(result)}")
            
            return result
        else:
            logger.warning("⚠️ Nenhum histórico encontrado")
            return []
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar histórico momentum v5.1.3: {str(e)}")
        return []

def validate_sopr_value(sopr: Optional[float]) -> bool:
    """
    NOVA FUNÇÃO v5.1.3: Valida valor SOPR
    
    Args:
        sopr: Valor SOPR para validar
        
    Returns:
        bool: True se válido ou None, False se inválido
    """
    if sopr is None:
        return True  # None é permitido
        
    # Range típico SOPR: 0.8 a 1.2 (com tolerância para extremos históricos)
    if not (0.5 <= sopr <= 1.5):
        logger.warning(f"⚠️ SOPR fora do range esperado: {sopr} (esperado: 0.5 a 1.5)")
        return False
        
    return True

def get_stats_sopr() -> Dict:
    """
    NOVA FUNÇÃO v5.1.3: Estatísticas do indicador SOPR
    """
    try:
        query = """
            SELECT 
                COUNT(*) as total_registros,
                COUNT(sopr) as registros_com_sopr,
                MIN(sopr) as sopr_min,
                MAX(sopr) as sopr_max,
                AVG(sopr) as sopr_media,
                MIN(timestamp) as primeiro_registro,
                MAX(timestamp) as ultimo_registro
            FROM indicadores_momentum
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            stats = dict(result)
            
            # Calcular percentual de cobertura SOPR
            total = stats.get('total_registros', 0)
            com_sopr = stats.get('registros_com_sopr', 0)
            stats['cobertura_sopr_percent'] = (com_sopr / total * 100) if total > 0 else 0
            
            logger.info(f"📈 Stats SOPR: {com_sopr}/{total} registros ({stats['cobertura_sopr_percent']:.1f}%)")
            return stats
        
        return {}
        
    except Exception as e:
        logger.error(f"❌ Erro calculando stats SOPR: {str(e)}")
        return {"erro": str(e)}

def debug_momentum_sopr():
    """
    NOVA FUNÇÃO v5.1.3: Debug específico do SOPR
    """
    try:
        logger.info("🔍 DEBUG v5.1.3: Verificando implementação SOPR...")
        
        # 1. Verificar se coluna existe
        query_coluna = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'indicadores_momentum' AND column_name = 'sopr'
        """
        
        coluna_existe = execute_query(query_coluna, fetch_one=True)
        logger.info(f"✅ Coluna SOPR existe: {coluna_existe is not None}")
        
        # 2. Stats básicas
        stats = get_stats_sopr()
        logger.info(f"📊 Stats SOPR: {stats}")
        
        # 3. Último registro
        ultimo = get_dados_momentum()
        if ultimo:
            sopr_value = ultimo.get('sopr')
            logger.info(f"📈 Último SOPR: {sopr_value} ({'OK' if validate_sopr_value(sopr_value) else 'INVÁLIDO'})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no debug SOPR: {str(e)}")
        return False

# FUNÇÕES LEGADAS MANTIDAS PARA COMPATIBILIDADE
def insert_dados_momentum_legacy(rsi: float, funding: float, netflow: float, ls_ratio: float, fonte: str = "Sistema") -> bool:
    """
    COMPATIBILIDADE: Função legada sem SOPR
    Redireciona para nova função com SOPR=None
    """
    logger.warning("⚠️ Usando função legada insert_dados_momentum_legacy - considere atualizar para incluir SOPR")
    return insert_dados_momentum(
        rsi=rsi,
        funding=funding,
        netflow=netflow,
        ls_ratio=ls_ratio,
        sopr=None,  # ← SOPR não fornecido na função legada
        fonte=fonte
    )