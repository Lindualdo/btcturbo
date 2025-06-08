# app/services/utils/__init__.py - CORRIGIDO v5.1.3

# Import centralizado via helpers (camada intermediária)
from .helpers import *

# Re-export para compatibilidade total
__all__ = [
    # Base PostgreSQL
    "get_db_connection", "execute_query", "test_connection",
    
    # Blocos individuais - v5.1.3 COMPLETO
    "get_dados_ciclo", "insert_dados_ciclo", "get_historico_ciclo",
    
    # FUNÇÕES NUPL v5.1.2 (mantidas)
    "validate_nupl_value", "get_stats_nupl", "debug_ciclo_nupl",
    
    # MOMENTUM + SOPR v5.1.3 (NOVAS)
    "get_dados_momentum", "insert_dados_momentum", "get_historico_momentum",
    "validate_sopr_value", "get_stats_sopr", "debug_momentum_sopr",
    "insert_dados_momentum_legacy",
    
    # Outros blocos (inalterados)
    "get_dados_risco", "insert_dados_risco_completo", "get_historico_risco",
    "get_dados_tecnico", "insert_dados_tecnico", "get_historico_tecnico",
    
    # Cache consolidado
    "get_score_cache_diario", "save_score_cache_diario", 
    "get_historico_scores", "limpar_cache_antigo",
    
    # Utils gerais
    "check_database_health", "get_all_latest_data", 
    "create_tables_if_not_exist", "insert_dados_exemplo"
]

# ==========================================
# CHANGELOG v5.1.3 - DEPLOY FIX
# ==========================================

"""
🔧 CORREÇÃO DEPLOY v5.1.3:

❌ PROBLEMA:
- Import direto de .postgres em /utils/__init__.py
- Cabeçalho incorreto copiado de /helpers/
- Estrutura de imports quebrada

✅ SOLUÇÃO:
- Import centralizado via .helpers
- Re-export de todas as funções necessárias
- Mantém compatibilidade total

🎯 RESULTADO:
- Deploy funciona corretamente
- Todas as funções SOPR v5.1.3 disponíveis
- Zero breaking changes para código existente
"""