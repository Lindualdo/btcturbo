
# app/services/utils/helpers/v2/dashboard_home/__init__.py
"""
Dashboard Home V2 - Arquitetura Otimizada

Fluxo:
1. data_collector.py      → UMA busca de todos os dados
2. cycle_analyzer.py      → Identifica ciclo de mercado  
3. setup_detector.py      → Detecta setup 4H
4. validation_gates.py    → Aplica gates de proteção
5. decision_matrix.py     → Matriz de decisão final
6. database_v2_helper.py  → Nova tabela otimizada

Características:
- Zero redundância de consultas
- Processamento sequencial 
- JSON simplificado (10-12 campos essenciais)
- Performance otimizada
- Reutilização total de funções existentes
"""

from .data_collector import collect_all_data