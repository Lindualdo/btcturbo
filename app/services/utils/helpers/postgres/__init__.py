# app/services/utils/helpers/postgres/__init__.py - v5.1.2 COM NUPL

# Imports da base
from .base import get_db_connection, execute_query, test_connection

# Imports específicos por bloco - v5.1.2 ATUALIZADO COM NUPL
from .ciclo_helper import (
    get_dados_ciclo, 
    insert_dados_ciclo,  # ← ATUALIZADO v5.1.2: agora aceita NUPL
    get_historico_ciclo,
    # NOVAS FUNÇÕES v5.1.2
    insert_dados_ciclo_legacy,  # ← NOVO: compatibilidade sem NUPL
    validate_nupl_value,        # ← NOVO: validação NUPL
    get_stats_nupl,            # ← NOVO: estatísticas NUPL
    debug_ciclo_nupl           # ← NOVO: debug específico NUPL
)

from .momentum_helper import get_dados_momentum, insert_dados_momentum, get_historico_momentum
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

# NOVO v5.1.2: Import dados exemplo com NUPL
from .dados_exemplo import (
    insert_dados_exemplo_realistas,  # ← ATUALIZADO: agora inclui NUPL
    limpar_dados_exemplo,
    get_dados_exemplo_nupl_stats     # ← NOVO: stats específicas NUPL
)

__all__ = [
    # Base
    "get_db_connection", "execute_query", "test_connection",
    
    # Blocos individuais - v5.1.2 ATUALIZADO
    "get_dados_ciclo", "insert_dados_ciclo", "get_historico_ciclo",
    
    # NOVAS FUNÇÕES NUPL v5.1.2
    "insert_dados_ciclo_legacy",      # ← NOVO: compatibilidade
    "validate_nupl_value",            # ← NOVO: validação NUPL
    "get_stats_nupl",                # ← NOVO: estatísticas NUPL
    "debug_ciclo_nupl",              # ← NOVO: debug NUPL
    
    # Outros blocos (sem alteração)
    "get_dados_momentum", "insert_dados_momentum", "get_historico_momentum",
    "get_dados_risco", "insert_dados_risco_completo", "get_historico_risco",
    "get_dados_tecnico", "insert_dados_tecnico", "get_historico_tecnico",
    
    # Cache consolidado
    "get_score_cache_diario", "save_score_cache_diario", 
    "get_historico_scores", "limpar_cache_antigo",
    
    # Utils
    "check_database_health", "get_all_latest_data", 
    "create_tables_if_not_exist", "insert_dados_exemplo",
    
    # NOVO v5.1.2: Dados exemplo com NUPL
    "insert_dados_exemplo_realistas",
    "limpar_dados_exemplo", 
    "get_dados_exemplo_nupl_stats"    # ← NOVO: stats NUPL
]

# ==========================================
# CHANGELOG v5.1.2
# ==========================================

"""
📋 MUDANÇAS v5.1.2:

✅ CICLO HELPER:
- insert_dados_ciclo() agora aceita parâmetro 'nupl' opcional
- get_dados_ciclo() retorna campo 'nupl'
- Novas funções: validate_nupl_value(), get_stats_nupl(), debug_ciclo_nupl()
- Função legada: insert_dados_ciclo_legacy() para compatibilidade

✅ DADOS EXEMPLO:
- insert_dados_exemplo_realistas() inclui valores NUPL nos cenários
- Nova função: get_dados_exemplo_nupl_stats() para análise

✅ COMPATIBILIDADE:
- Todos os imports existentes continuam funcionando
- Sistema funciona com NUPL=NULL para registros antigos
- Função legada mantém compatibilidade total

🎯 PRÓXIMOS PASSOS:
- Atualizar indicadores/ciclos.py para retornar NUPL
- Implementar score NUPL em scores/ciclos.py
- Rebalancear pesos: MVRV 50%→30%, NUPL 20%
"""