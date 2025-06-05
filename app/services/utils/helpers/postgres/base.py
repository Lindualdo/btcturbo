# app/services/utils/helpers/postgres/base.py

import logging
from datetime import datetime
from typing import Dict, Optional, List, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import OperationalError, DatabaseError
from app.config import get_settings

# Configurar logging específico para PostgreSQL
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """
    Conecta com PostgreSQL usando configurações do Railway
    Prioriza configurações separadas (DB_HOST, DB_NAME, etc.)
    """
    settings = get_settings()
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # FORÇAR USO DAS CONFIGURAÇÕES SEPARADAS (Railway)
            if settings.DB_HOST and settings.DB_NAME and settings.DB_USER and settings.DB_PASSWORD:
                logger.info("🔗 Conectando via configurações separadas (Railway)")
                conn = psycopg2.connect(
                    host=settings.DB_HOST,
                    database=settings.DB_NAME,
                    user=settings.DB_USER,
                    password=settings.DB_PASSWORD,
                    port=settings.DB_PORT,
                    cursor_factory=RealDictCursor,
                    connect_timeout=10
                )
            elif settings.DATABASE_URL:
                logger.info("🔗 Conectando via DATABASE_URL")
                conn = psycopg2.connect(
                    settings.DATABASE_URL,
                    cursor_factory=RealDictCursor,
                    connect_timeout=10
                )
            else:
                raise Exception("❌ Nenhuma configuração PostgreSQL encontrada")
            
            # Testar conexão
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                
            logger.info("✅ Conexão PostgreSQL estabelecida com sucesso")
            return conn
            
        except OperationalError as e:
            retry_count += 1
            logger.warning(f"❌ Tentativa {retry_count}/{max_retries} falhou: {str(e)}")
            
            if retry_count >= max_retries:
                logger.error("🚨 ERRO CRÍTICO: Não foi possível conectar ao PostgreSQL após 3 tentativas")
                logger.error(f"🔍 Configurações: HOST={settings.DB_HOST}, DB={settings.DB_NAME}, USER={settings.DB_USER}")
                raise Exception(f"Falha na conexão PostgreSQL: {str(e)}")
                
        except Exception as e:
            logger.error(f"🚨 Erro inesperado na conexão: {str(e)}")
            raise

def execute_query(query: str, params: tuple = None, fetch_one: bool = False, fetch_all: bool = False):
    """
    Executa query com tratamento robusto de erros
    Função genérica reutilizada por todos os helpers
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                
                if fetch_one:
                    result = cursor.fetchone()
                    return dict(result) if result else None
                elif fetch_all:
                    results = cursor.fetchall()
                    return [dict(row) for row in results] if results else []
                else:
                    conn.commit()
                    return {"status": "success", "affected_rows": cursor.rowcount}
                    
    except DatabaseError as e:
        logger.error(f"🚨 Erro na execução da query: {str(e)}")
        logger.error(f"Query: {query}")
        logger.error(f"Params: {params}")
        raise Exception(f"Erro no banco de dados: {str(e)}")
    except Exception as e:
        logger.error(f"🚨 Erro inesperado: {str(e)}")
        raise

def test_connection() -> bool:
    """Testa conexão básica com o PostgreSQL"""
    try:
        logger.info("🧪 Testando conexão PostgreSQL...")
        
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT version()")
                version = cursor.fetchone()
                
                # Fix: version é um dict devido ao RealDictCursor
                if version:
                    version_str = str(version.get('version', 'Unknown')) if isinstance(version, dict) else str(version)
                    logger.info(f"✅ PostgreSQL conectado: {version_str}")
                else:
                    logger.info("✅ PostgreSQL conectado: Version query returned empty")
                    
                return True
                
    except Exception as e:
        logger.error(f"❌ Teste de conexão falhou: {str(e)}")
        return False