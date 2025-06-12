# app/services/utils/helpers/dashboard_home/__init__.py - ATUALIZADO

"""
Dashboard Home Helpers - Arquitetura Modular v2 COM ESTRATÉGIA

Estrutura:
├── header_helper.py      # Cabeçalho (4 campos)
├── mercado_helper.py     # Score Mercado (4 campos)
├── risco_helper.py       # Score Risco (4 campos)
├── alavancagem_helper.py # Gestão Alavancagem (6 campos)
├── estrategia_helper.py  # Estratégia Tática (8 campos) ← NOVO
├── aggregator.py         # Orquestrador
└── database_helper.py    # CRUD PostgreSQL

Fluxo:
aggregator → helpers → database → response

TOTAL: 26 campos + JSON consolidado com 5 módulos
"""

from .aggregator import collect_all_dashboard_data
from ..postgres.dash_home_helper import insert_dashboard_data, get_latest_dashboard
from .header_helper import get_header_data
from .mercado_helper import get_mercado_data
from .risco_helper import get_risco_data
from .alavancagem_helper import get_alavancagem_data
from .estrategia_helper import get_estrategia_data  # ← NOVO