# app/services/utils/helpers/postgres/__init__.py

"""
PostgreSQL Helpers - BTC Turbo
Estrutura organizada por blocos para facilitar manutenção
"""

# Imports da base (conexão e função genérica)
from .base import get_db_connection, execute_query, test_connection

# Imports específicos por bloco
from .ciclo_helper import get_dados_ciclo, insert_dados_ciclo, get_historico_ciclo
from .momentum_helper import get_dados_momentum, insert_dados_momentum, get_historico_momentum
from .risco_helper import get_dados_risco, insert_dados_risco, get_historico_risco
from .tecnico_helper import get_dados_tecnico, insert_dados_tecnico, get_historico_tecnico

# Imports utilitários
from .utils import (
    check_database_health, 
    get_all_latest_data, 
    create_tables_if_not_exist,
    insert_dados_exemplo
)

# Facilita uso: from app.services.utils.helpers.postgres import get_dados_ciclo
__all__ = [
    # Base
    "get_db_connection", "execute_query", "test_connection",
    
    # Ciclo
    "get_dados_ciclo", "insert_dados_ciclo", "get_historico_ciclo",
    
    # Momentum  
    "get_dados_momentum", "insert_dados_momentum", "get_historico_momentum",
    
    # Risco
    "get_dados_risco", "insert_dados_risco", "get_historico_risco",
    
    # Técnico
    "get_dados_tecnico", "insert_dados_tecnico", "get_historico_tecnico",
    
    # Utils
    "check_database_health", "get_all_latest_data", 
    "create_tables_if_not_exist", "insert_dados_exemplo"
]