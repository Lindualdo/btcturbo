# app/services/utils/helpers/__init__.py - v5.1.3 COMPATIBILIDADE SOPR

# Imports da base (postgres/)
from .postgres.base import get_db_connection, execute_query, test_connection

# Imports específicos por bloco - v5.1.3 MOMENTUM ATUALIZADO
from .postgres.ciclo_helper import (
    get_dados_ciclo,              # ← v5.1.2: retorna NUPL
    insert_dados_ciclo,           # ← v5.1.2: aceita NUPL opcional
    get_historico_ciclo,          # ← v5.1.2: inclui NUPL
    # FUNÇÕES NUPL v5.1.2
    validate_nupl_value,          
    get_stats_nupl,              
    debug_ciclo_nupl             
)

from .postgres.momentum_helper import (
    get_dados_momentum,           # ← v5.1.3: retorna SOPR
    insert_dados_momentum,        # ← v5.1.3: aceita SOPR opcional
    get_historico_momentum,       # ← v5.1.3: inclui SOPR
    # NOVAS FUNÇÕES SOPR v5.1.3
    validate_sopr_value,          # ← NOVO v5.1.3
    get_stats_sopr,              # ← NOVO v5.1.3
    debug_momentum_sopr,         # ← NOVO v5.1.3
    insert_dados_momentum_legacy  # ← NOVO v5.1.3: compatibilidade
)

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
    
    # Blocos individuais - v5.1.3 COM SOPR
    "get_dados_ciclo", "insert_dados_ciclo", "get_historico_ciclo",
    
    # FUNÇÕES NUPL v5.1.2 (mantidas)
    "validate_nupl_value", "get_stats_nupl", "debug_ciclo_nupl",
    
    # MOMENTUM v5.1.3 - COM SOPR
    "get_dados_momentum", "insert_dados_momentum", "get_historico_momentum",
    
    # NOVAS FUNÇÕES SOPR v5.1.3
    "validate_sopr_value", "get_stats_sopr", "debug_momentum_sopr",
    "insert_dados_momentum_legacy",
    
    # Outros blocos (inalterados)
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
# NOTA v5.1.3: COMPATIBILIDADE SOPR
# ==========================================

"""
✅ TODAS as funções existentes continuam funcionando igual
✅ Código existente não precisa ser alterado
✅ SOPR é opcional - sistema funciona sem ele
✅ Exchange_Netflow mantido no DB para compatibilidade
✅ Novos recursos disponíveis para quem quiser usar

🔧 MIGRAÇÃO GRADUAL v5.1.3:
1. Sistema funciona normalmente (SOPR=NULL para registros antigos)
2. Notion pode ser configurado para incluir SOPR quando conveniente  
3. Scores são calculados automaticamente considerando SOPR quando disponível
4. APIs mostram SOPR em vez de Exchange_Netflow quando presente
5. Exchange_Netflow continua no DB mas não aparece nas APIs
"""