# app/services/utils/helpers/postgres_helper.py

import logging
from datetime import datetime
from typing import Dict, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import get_settings

def get_db_connection():
    """Conecta com PostgreSQL usando configurações do .env"""
    settings = get_settings()
    return psycopg2.connect(
        host=settings.DB_HOST,
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        cursor_factory=RealDictCursor
    )

# ==========================================
# FUNÇÕES BLOCO CICLO
# ==========================================

def get_dados_ciclo() -> Optional[Dict]:
    """Busca dados mais recentes do bloco ciclo"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT mvrv_z_score, realized_ratio, puell_multiple, 
                           timestamp, fonte, metadados
                    FROM indicadores_ciclo 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """
                cursor.execute(query)
                result = cursor.fetchone()
                return dict(result) if result else None
                
    except Exception as e:
        logging.error(f"Erro ao buscar dados do bloco ciclo: {str(e)}")
        return None

