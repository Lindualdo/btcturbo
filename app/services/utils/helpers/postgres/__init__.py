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
    get_historico_momentum,  # ← v5.1.3: inclui SOPR
    # NOVAS FUNÇÕES SOPR v5.1.3
    validate_sopr_value,        # ← NOVO v5.1.3
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

# v5.1.3: Import dados exemplo com SOPR
from .dados_exemplo import (
    insert_dados_exemplo_realistas,  # ← v5.1.2: inclui NUPL, v5.1.3: incluirá SOPR
    limpar_dados_exemplo,
    get_dados_exemplo_nupl_stats     # ← v5.1.2: stats NUPL
)

__all__ = [
    # Base
    "get_db_connection", "execute_query", "test_connection",
    
    # Blocos individuais - v5.1.3 ATUALIZADO
    "get_dados_ciclo", "insert_dados_ciclo", "get_historico_ciclo",
    
    # FUNÇÕES NUPL v5.1.2 (mantidas)
    "insert_dados_ciclo_legacy",      
      
             
         
    
    # MOMENTUM v5.1.3 - COM SOPR
    "get_dados_momentum", "insert_dados_momentum", "get_historico_momentum",
    
    # NOVAS FUNÇÕES SOPR v5.1.3
    "validate_sopr_value",            # ← NOVO: validação SOPR
    "get_stats_sopr",                # ← NOVO: estatísticas SOPR
    "debug_momentum_sopr",           # ← NOVO: debug SOPR
    "insert_dados_momentum_legacy",  # ← NOVO: compatibilidade sem SOPR
    
    # Outros blocos (sem alteração)
    "get_dados_risco", "insert_dados_risco_completo", "get_historico_risco",
    "get_dados_tecnico", "insert_dados_tecnico", "get_historico_tecnico",
    
    # Cache consolidado
    "get_score_cache_diario", "save_score_cache_diario", 
    "get_historico_scores", "limpar_cache_antigo",
    
    # Utils
    "check_database_health", "get_all_latest_data", 
    "create_tables_if_not_exist", "insert_dados_exemplo",
    
    # Dados exemplo
    "insert_dados_exemplo_realistas",
    "limpar_dados_exemplo", 
    "get_dados_exemplo_nupl_stats"
]

# ==========================================
# CHANGELOG v5.1.3
# ==========================================

"""
📋 MUDANÇAS v5.1.3:

✅ MOMENTUM HELPER:
- insert_dados_momentum() agora aceita parâmetro 'sopr' opcional
- get_dados_momentum() retorna campo 'sopr'  
- Novas funções: validate_sopr_value(), get_stats_sopr(), debug_momentum_sopr()
- Função legada: insert_dados_momentum_legacy() para compatibilidade
- Exchange_netflow mantido no DB mas removido das APIs

✅ COMPATIBILIDADE:
- Todos os imports existentes continuam funcionando
- Sistema funciona com SOPR=NULL para registros antigos
- Função legada mantém compatibilidade total
- Exchange_Netflow preservado no banco de dados

🎯 PRÓXIMOS PASSOS v5.1.3:
- ✅ Atualizar indicadores/momentum.py para retornar SOPR
- ✅ Implementar score SOPR em scores/momentum.py  
- ✅ Substituir Exchange_Netflow por SOPR nas APIs
- ⏳ Atualizar dados exemplo para incluir SOPR
- ⏳ Executar migration SQL em produção
"""