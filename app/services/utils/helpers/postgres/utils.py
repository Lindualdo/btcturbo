# app/services/utils/helpers/postgres/utils.py

import logging
from datetime import datetime
from typing import Dict
from .base import execute_query
from .indicadores.ciclo_helper import get_dados_ciclo
from .indicadores.momentum_helper import get_dados_momentum
from .indicadores.risco_helper import get_dados_risco
from .indicadores.tecnico_helper import get_dados_tecnico

logger = logging.getLogger(__name__)

def check_database_health() -> Dict:
    """Verifica saúde do banco e retorna estatísticas"""
    try:
        logger.info("🏥 Verificando saúde do banco de dados...")
        
        queries = {
            "ciclo": "SELECT COUNT(*) as total, MAX(timestamp) as last_update FROM indicadores_ciclo",
            "momentum": "SELECT COUNT(*) as total, MAX(timestamp) as last_update FROM indicadores_momentum", 
            "risco": "SELECT COUNT(*) as total, MAX(timestamp) as last_update FROM indicadores_risco",
            "tecnico": "SELECT COUNT(*) as total, MAX(timestamp) as last_update FROM indicadores_tecnico"
        }
        
        health_status = {}
        
        for bloco, query in queries.items():
            try:
                result = execute_query(query, fetch_one=True)
                health_status[bloco] = {
                    "total_records": result['total'],
                    "last_update": result['last_update'].isoformat() if result['last_update'] else None,
                    "status": "✅ OK" if result['total'] > 0 else "⚠️ VAZIO"
                }
            except Exception as e:
                health_status[bloco] = {
                    "status": f"❌ ERRO: {str(e)}",
                    "total_records": 0,
                    "last_update": None
                }
        
        logger.info("✅ Verificação de saúde concluída")
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "database_status": "CONECTADO",
            "blocos": health_status
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na verificação de saúde: {str(e)}")
        return {
            "timestamp": datetime.utcnow().isoformat(), 
            "database_status": "ERRO",
            "error": str(e)
        }

def get_all_latest_data() -> Dict:
    """Busca dados mais recentes de todos os blocos"""
    try:
        logger.info("📊 Buscando dados mais recentes de todos os blocos...")
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "ciclo": get_dados_ciclo(),
            "momentum": get_dados_momentum(), 
            "risco": get_dados_risco(),
            "tecnico": get_dados_tecnico()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar todos os dados: {str(e)}")
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

def create_tables_if_not_exist():
    """Cria tabelas se não existirem (útil para desenvolvimento)"""
    try:
        logger.info("🔧 Verificando/criando tabelas...")
        
        tables_sql = """
        CREATE TABLE IF NOT EXISTS indicadores_ciclo (
            id SERIAL PRIMARY KEY,
            mvrv_z_score DECIMAL(15,6),
            realized_ratio DECIMAL(15,6), 
            puell_multiple DECIMAL(15,6),
            timestamp TIMESTAMP DEFAULT NOW(),
            fonte VARCHAR(50) DEFAULT 'Sistema',
            metadados JSONB DEFAULT '{}'
        );
        
        CREATE TABLE IF NOT EXISTS indicadores_momentum (
            id SERIAL PRIMARY KEY,
            rsi_semanal DECIMAL(15,6),
            funding_rates DECIMAL(15,6),
            oi_change DECIMAL(15,6),
            long_short_ratio DECIMAL(15,6),
            timestamp TIMESTAMP DEFAULT NOW(),
            fonte VARCHAR(50) DEFAULT 'Sistema',
            metadados JSONB DEFAULT '{}'
        );
        
        CREATE TABLE IF NOT EXISTS indicadores_risco (
            id SERIAL PRIMARY KEY,
            dist_liquidacao DECIMAL(15,6),
            health_factor DECIMAL(15,6),
            exchange_netflow DECIMAL(15,6),
            stablecoin_ratio DECIMAL(15,6),
            timestamp TIMESTAMP DEFAULT NOW(),
            fonte VARCHAR(50) DEFAULT 'Sistema',
            metadados JSONB DEFAULT '{}'
        );
        
        CREATE TABLE IF NOT EXISTS indicadores_tecnico (
            id SERIAL PRIMARY KEY,
            sistema_emas DECIMAL(15,6),
            padroes_graficos DECIMAL(15,6),
            timestamp TIMESTAMP DEFAULT NOW(),
            fonte VARCHAR(50) DEFAULT 'Sistema',
            metadados JSONB DEFAULT '{}'
        );
        """
        
        execute_query(tables_sql)
        logger.info("✅ Tabelas verificadas/criadas com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {str(e)}")
        return False

def insert_dados_exemplo():
    """Insere dados de exemplo para teste (desenvolvimento)"""
    try:
        from .dados_exemplo import insert_dados_exemplo_realistas
        return insert_dados_exemplo_realistas()
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dados exemplo: {str(e)}")
        return False