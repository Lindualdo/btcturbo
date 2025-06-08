# app/services/utils/helpers/postgres/ciclo_helper.py - v5.1.2 COM NUPL

import logging
from datetime import datetime
from typing import Dict, Optional
from .base import execute_query

logger = logging.getLogger(__name__)

def get_dados_ciclo() -> Optional[Dict]:
    """
    Busca dados mais recentes do bloco ciclo - ATUALIZADO v5.1.2 com NUPL
    """
    try:
        logger.info("🔍 Buscando dados do bloco CICLO (incluindo NUPL)...")
        
        query = """
            SELECT mvrv_z_score, realized_ratio, puell_multiple, nupl,
                   timestamp, fonte, metadados
            FROM indicadores_ciclo 
            ORDER BY timestamp DESC 
            LIMIT 1
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            # LOG detalhado para v5.1.2
            logger.info(f"✅ Dados ciclo encontrados:")
            logger.info(f"    MVRV: {result.get('mvrv_z_score')}")
            logger.info(f"    Realized: {result.get('realized_ratio')}")
            logger.info(f"    Puell: {result.get('puell_multiple')}")
            logger.info(f"    NUPL: {result.get('nupl')} ← NOVO v5.1.2")
            logger.info(f"    Timestamp: {result['timestamp']}")
            
            return result
        else:
            logger.warning("⚠️ Nenhum dado encontrado na tabela indicadores_ciclo")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar dados do bloco ciclo: {str(e)}")
        return None

def insert_dados_ciclo(
    mvrv_z: float, 
    realized_ratio: float, 
    puell_multiple: float, 
    nupl: Optional[float] = None,  # ← NOVO v5.1.2
    fonte: str = "Sistema"
) -> bool:
    """
    Insere novos dados no bloco ciclo - ATUALIZADO v5.1.2 com NUPL
    
    Args:
        mvrv_z: MVRV Z-Score
        realized_ratio: Realized Price Ratio  
        puell_multiple: Puell Multiple
        nupl: Net Unrealized Profit/Loss (NOVO v5.1.2) - Opcional
        fonte: Fonte dos dados
    
    Returns:
        bool: Sucesso da operação
    """
    try:
        logger.info(f"💾 Inserindo dados ciclo v5.1.2:")
        logger.info(f"    MVRV={mvrv_z}, Realized={realized_ratio}")
        logger.info(f"    Puell={puell_multiple}, NUPL={nupl} ← NOVO")
        
        query = """
            INSERT INTO indicadores_ciclo 
            (mvrv_z_score, realized_ratio, puell_multiple, nupl, fonte, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        params = (
            mvrv_z, 
            realized_ratio, 
            puell_multiple, 
            nupl,  # ← NOVO: pode ser None
            fonte, 
            datetime.utcnow()
        )
        
        execute_query(query, params)
        logger.info("✅ Dados ciclo v5.1.2 inseridos com sucesso (incluindo NUPL)")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dados ciclo v5.1.2: {str(e)}")
        return False

def get_historico_ciclo(limit: int = 10) -> list:
    """
    Busca histórico de dados do bloco ciclo - ATUALIZADO v5.1.2 com NUPL
    """
    try:
        logger.info(f"📊 Buscando histórico do bloco CICLO v5.1.2 (últimos {limit} registros)")
        
        query = """
            SELECT mvrv_z_score, realized_ratio, puell_multiple, nupl,
                   timestamp, fonte
            FROM indicadores_ciclo 
            ORDER BY timestamp DESC 
            LIMIT %s
        """
        
        result = execute_query(query, params=(limit,), fetch_all=True)
        
        if result:
            logger.info(f"✅ {len(result)} registros históricos encontrados (com NUPL)")
            
            # LOG estatísticas NUPL para debug v5.1.2
            nupl_count = sum(1 for r in result if r.get('nupl') is not None)
            logger.info(f"📈 Registros com NUPL: {nupl_count}/{len(result)}")
            
            return result
        else:
            logger.warning("⚠️ Nenhum histórico encontrado")
            return []
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar histórico ciclo v5.1.2: {str(e)}")
        return []

def insert_dados_ciclo_legacy(mvrv_z: float, realized_ratio: float, puell_multiple: float, fonte: str = "Sistema") -> bool:
    """
    COMPATIBILIDADE: Função legada sem NUPL
    Redireciona para nova função com NUPL=None
    """
    logger.warning("⚠️ Usando função legada insert_dados_ciclo_legacy - considere atualizar para incluir NUPL")
    return insert_dados_ciclo(
        mvrv_z=mvrv_z,
        realized_ratio=realized_ratio, 
        puell_multiple=puell_multiple,
        nupl=None,  # ← NUPL não fornecido na função legada
        fonte=fonte
    )

def validate_nupl_value(nupl: Optional[float]) -> bool:
    """
    NOVA FUNÇÃO v5.1.2: Valida valor NUPL
    
    Args:
        nupl: Valor NUPL para validar
        
    Returns:
        bool: True se válido ou None, False se inválido
    """
    if nupl is None:
        return True  # None é permitido
        
    # Range típico NUPL: -0.5 a 1.2 (com tolerância)
    if not (-0.5 <= nupl <= 1.2):
        logger.warning(f"⚠️ NUPL fora do range esperado: {nupl} (esperado: -0.5 a 1.2)")
        return False
        
    return True

def get_stats_nupl() -> Dict:
    """
    NOVA FUNÇÃO v5.1.2: Estatísticas do indicador NUPL
    Útil para monitoramento e debug
    """
    try:
        query = """
            SELECT 
                COUNT(*) as total_registros,
                COUNT(nupl) as registros_com_nupl,
                MIN(nupl) as nupl_min,
                MAX(nupl) as nupl_max,
                AVG(nupl) as nupl_media,
                MIN(timestamp) as primeiro_registro,
                MAX(timestamp) as ultimo_registro
            FROM indicadores_ciclo
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            stats = dict(result)
            
            # Calcular percentual de cobertura NUPL
            total = stats.get('total_registros', 0)
            com_nupl = stats.get('registros_com_nupl', 0)
            stats['cobertura_nupl_percent'] = (com_nupl / total * 100) if total > 0 else 0
            
            logger.info(f"📈 Stats NUPL: {com_nupl}/{total} registros ({stats['cobertura_nupl_percent']:.1f}%)")
            return stats
        
        return {}
        
    except Exception as e:
        logger.error(f"❌ Erro calculando stats NUPL: {str(e)}")
        return {"erro": str(e)}

# ==========================================
# LOGS E DEBUG v5.1.2
# ==========================================

def debug_ciclo_nupl():
    """
    FUNÇÃO DEBUG v5.1.2: Diagnóstico específico do NUPL
    """
    try:
        logger.info("🔍 DEBUG v5.1.2: Verificando implementação NUPL...")
        
        # 1. Verificar se coluna existe
        query_coluna = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'indicadores_ciclo' AND column_name = 'nupl'
        """
        
        coluna_existe = execute_query(query_coluna, fetch_one=True)
        logger.info(f"✅ Coluna NUPL existe: {coluna_existe is not None}")
        
        # 2. Stats básicas
        stats = get_stats_nupl()
        logger.info(f"📊 Stats NUPL: {stats}")
        
        # 3. Último registro
        ultimo = get_dados_ciclo()
        if ultimo:
            nupl_value = ultimo.get('nupl')
            logger.info(f"📈 Último NUPL: {nupl_value} ({'OK' if validate_nupl_value(nupl_value) else 'INVÁLIDO'})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no debug NUPL: {str(e)}")
        return False