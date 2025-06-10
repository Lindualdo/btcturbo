# app/services/utils/helpers/postgres/__init__.py - v5.1.3 COM SOPR

# Imports da base
from .base import get_db_connection, execute_query, test_connection

# Imports específicos por bloco - v5.1.3 ATUALIZADO COM SOPR
from .ciclo_helper import (
    get_dados_ciclo, 
    insert_dados_ciclo,  # ← v5.1.2: agora aceita NUPL
    get_historico_ciclo,
    # FUNÇÕES NUPL v5.1.2
    insert_dados_ciclo_legacy     
)

from .momentum_helper import (
    get_dados_momentum,  # ← v5.1.3: agora retorna SOPR
    insert_dados_momentum,  # ← v5.1.3: agora aceita SOPR
    # NOVAS FUNÇÕES SOPR v5.1.3

    get_stats_sopr,            # ← NOVO v5.1.3
    debug_momentum_sopr,       # ← NOVO v5.1.3
    insert_dados_momentum_legacy  # ← NOVO v5.1.3: compatibilidade
)

from .risco_helper import get_dados_risco, insert_dados_risco_completo, get_historico_risco
from .tecnico_helper import get_dados_tecnico, insert_dados_tecnico, get_historico_tecnico

# Import cache consolidado
from .scores_consolidados_helper import (
    get_score_cache_diario, save_score_cache_diario, 
    get_historico_scores, limpar_cache_antigo
)

# Imports utilitários
from .utils import (
    check_database_health, get_all_latest_data, 
    create_tables_if_not_exist, insert_dados_exemplo
)