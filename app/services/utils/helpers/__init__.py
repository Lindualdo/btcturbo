# app/services/utils/helpers/__init__.py

# Imports da base (postgres/)
from .postgres.base import get_db_connection, execute_query, test_connection

# Imports específicos por bloco
from .postgres.ciclo_helper import get_dados_ciclo, insert_dados_ciclo, get_historico_ciclo
from .postgres.momentum_helper import get_dados_momentum, insert_dados_momentum, get_historico_momentum
from .postgres.risco_helper import get_dados_risco, insert_dados_risco_completo, get_historico_risco
from .postgres.tecnico_helper import get_dados_tecnico, insert_dados_tecnico, get_historico_tecnico

# Import cache consolidado
from .postgres.scores_consolidados_helper import (
    get_score_cache_diario, save_score_cache_diario, 
    get_historico_scores, limpar_cache_antigo
)

# Imports utilitários
from .postgres.utils import (
    check_database_health, get_all_latest_data, 
    create_tables_if_not_exist, insert_dados_exemplo
)

__all__ = [
    # Base
    "get_db_connection", "execute_query", "test_connection",
    
    # Blocos individuais
    "get_dados_ciclo", "insert_dados_ciclo", "get_historico_ciclo",
    "get_dados_momentum", "insert_dados_momentum", "get_historico_momentum",
    "get_dados_risco", "insert_dados_risco_completo", "get_historico_risco",
    "get_dados_tecnico", "insert_dados_tecnico", "get_historico_tecnico",
    
    # Cache consolidado
    "get_score_cache_diario", "save_score_cache_diario", 
    "get_historico_scores", "limpar_cache_antigo",
    
    # Utils
    "check_database_health", "get_all_latest_data", 
    "create_tables_if_not_exist", "insert_dados_exemplo"
]