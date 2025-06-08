# app/services/utils/helpers/__init__.py - v5.1.2 COMPATIBILIDADE NUPL

# Imports da base (postgres/)
from .postgres.base import get_db_connection, execute_query, test_connection

# Imports específicos por bloco - v5.1.2 ATUALIZADOS
from .postgres.ciclo_helper import (
    get_dados_ciclo,              # ← ATUALIZADO: retorna NUPL
    insert_dados_ciclo,           # ← ATUALIZADO: aceita NUPL opcional
    get_historico_ciclo,          # ← ATUALIZADO: inclui NUPL
    # NOVAS FUNÇÕES v5.1.2 NUPL
    validate_nupl_value,          # ← NOVO
    get_stats_nupl,              # ← NOVO  
    debug_ciclo_nupl             # ← NOVO
)

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
    
    # Blocos individuais - v5.1.2 COM NUPL
    "get_dados_ciclo", "insert_dados_ciclo", "get_historico_ciclo",
    
    # NOVAS FUNÇÕES NUPL v5.1.2
    "validate_nupl_value", "get_stats_nupl", "debug_ciclo_nupl",
    
    # Outros blocos (inalterados)
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

# ==========================================
# NOTA v5.1.2: COMPATIBILIDADE
# ==========================================

"""
✅ TODAS as funções existentes continuam funcionando igual
✅ Código existente não precisa ser alterado
✅ NUPL é opcional - sistema funciona sem ele
✅ Novos recursos disponíveis para quem quiser usar

🔧 MIGRAÇÃO GRADUAL:
1. Sistema funciona normalmente (NUPL=NULL para registros antigos)
2. Notion pode ser configurado para incluir NUPL quando conveniente  
3. Scores são calculados automaticamente considerando NUPL quando disponível
4. Dashboards mostram NUPL quando presente
"""