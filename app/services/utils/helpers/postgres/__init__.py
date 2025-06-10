# app/services/utils/helpers/postgres/__init__.py - ADICIONAR

# Imports da base
from .base import get_db_connection, execute_query, test_connection

# Imports específicos por bloco
from .ciclo_helper import get_dados_ciclo, insert_dados_ciclo, get_historico_ciclo
from .momentum_helper import get_dados_momentum, insert_dados_momentum
from .risco_helper import get_dados_risco, insert_dados_risco_completo, get_historico_risco
from .tecnico_helper import get_dados_tecnico, insert_dados_tecnico, get_historico_tecnico

# Import cache consolidado
from .scores_consolidados_helper import (
    get_score_cache_diario, save_score_cache_diario, 
    get_historico_scores, limpar_cache_antigo
)

# Dashboard Home agora está em dashboard_home/ (modular)
# Removido: dashboard_home_helper (substituído por arquitetura modular)

# Imports utilitários
from .utils import (
    check_database_health, get_all_latest_data, 
    create_tables_if_not_exist, insert_dados_exemplo
)