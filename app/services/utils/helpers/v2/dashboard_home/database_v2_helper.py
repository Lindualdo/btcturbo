# app/services/utils/helpers/v2/dashboard_home/database_v2_helper.py

import logging
import json
from datetime import datetime
from typing import Dict, Optional
from app.services.utils.helpers.postgres.base import execute_query

logger = logging.getLogger(__name__)

def save_dashboard_v2(dashboard_data: Dict) -> bool:
    """
    Salva dashboard V2 no PostgreSQL
    
    Args:
        dashboard_data: Dict com campos + json
    
    Returns:
        bool: Sucesso da operação
    """
    try:
        logger.info("💾 Salvando Dashboard V2...")
        
        # Criar tabela se não existir
        _create_table_if_not_exists()
        
        campos = dashboard_data["campos"]
        dashboard_json = dashboard_data["json"]
        
        # Query de inserção
        query = """
            INSERT INTO dashboard_decisao_v2 (
                btc_price, score_mercado, score_risco, ciclo_atual, 
                setup_4h, decisao_final, alavancagem_atual, health_factor,
                ema_distance, rsi_diario, dashboard_json, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        valores = (
            campos["btc_price"],
            campos["score_mercado"], 
            campos["score_risco"],
            campos["ciclo_atual"],
            campos["setup_4h"],
            campos["decisao_final"],
            campos["alavancagem_atual"],
            campos["health_factor"],
            campos["ema_distance"],
            campos["rsi_diario"],
            json.dumps(dashboard_json),
            datetime.utcnow()
        )
        
        execute_query(query, valores)
        
        logger.info("✅ Dashboard V2 salvo com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro salvando Dashboard V2: {str(e)}")
        return False

def get_latest_dashboard_v2() -> Optional[Dict]:
    """
    Busca último dashboard V2
    
    Returns:
        Dict com dados ou None se não encontrado
    """
    try:
        logger.info("🔍 Buscando último Dashboard V2...")
        
        query = """
            SELECT * FROM dashboard_decisao_v2 
            ORDER BY created_at DESC 
            LIMIT 1
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            logger.info(f"✅ Dashboard V2 encontrado: ID {result['id']}")
            return result
        else:
            logger.warning("⚠️ Nenhum Dashboard V2 encontrado")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro buscando Dashboard V2: {str(e)}")
        return None

def get_dashboard_v2_history(limit: int = 10) -> list:
    """
    Busca histórico de dashboards V2
    
    Args:
        limit: Número máximo de registros
    
    Returns:
        Lista com histórico
    """
    try:
        query = """
            SELECT id, ciclo_atual, decisao_final, btc_price, 
                   score_mercado, score_risco, created_at
            FROM dashboard_decisao_v2 
            ORDER BY created_at DESC 
            LIMIT %s
        """
        
        results = execute_query(query, (limit,), fetch_all=True)
        
        return results if results else []
        
    except Exception as e:
        logger.error(f"❌ Erro buscando histórico V2: {str(e)}")
        return []

def cleanup_old_records_v2(days_to_keep: int = 30) -> bool:
    """
    Remove registros antigos para manter performance
    
    Args:
        days_to_keep: Dias para manter
    
    Returns:
        bool: Sucesso da operação
    """
    try:
        query = """
            DELETE FROM dashboard_decisao_v2 
            WHERE created_at < NOW() - INTERVAL '%s days'
        """
        
        execute_query(query, (days_to_keep,))
        
        logger.info(f"✅ Limpeza V2 concluída (mantidos últimos {days_to_keep} dias)")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na limpeza V2: {str(e)}")
        return False

def _create_table_if_not_exists():
    """
    Cria tabela dashboard_decisao_v2 se não existir
    """
    try:
        query = """
            CREATE TABLE IF NOT EXISTS dashboard_decisao_v2 (
                id SERIAL PRIMARY KEY,
                btc_price DECIMAL(10,2) NOT NULL,
                score_mercado DECIMAL(5,1) NOT NULL,
                score_risco DECIMAL(5,1) NOT NULL,
                ciclo_atual VARCHAR(20) NOT NULL,
                setup_4h VARCHAR(30) NOT NULL,
                decisao_final VARCHAR(30) NOT NULL,
                alavancagem_atual DECIMAL(3,1) NOT NULL,
                health_factor DECIMAL(4,2) NOT NULL,
                ema_distance DECIMAL(6,2) NOT NULL,
                rsi_diario DECIMAL(5,1) NOT NULL,
                dashboard_json JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Índices para performance
                INDEX idx_dashboard_v2_created_at (created_at DESC),
                INDEX idx_dashboard_v2_ciclo (ciclo_atual),
                INDEX idx_dashboard_v2_decisao (decisao_final)
            )
        """
        
        execute_query(query)
        logger.info("✅ Tabela dashboard_decisao_v2 verificada/criada")
        
    except Exception as e:
        logger.error(f"❌ Erro criando tabela V2: {str(e)}")
        raise

def get_dashboard_v2_stats() -> Dict:
    """
    Estatísticas da tabela V2
    
    Returns:
        Dict com estatísticas
    """
    try:
        query = """
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT ciclo_atual) as ciclos_unicos,
                COUNT(DISTINCT decisao_final) as decisoes_unicas,
                MIN(created_at) as primeiro_registro,
                MAX(created_at) as ultimo_registro
            FROM dashboard_decisao_v2
        """
        
        result = execute_query(query, fetch_one=True)
        
        return result if result else {}
        
    except Exception as e:
        logger.error(f"❌ Erro estatísticas V2: {str(e)}")
        return {}