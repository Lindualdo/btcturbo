# app/services/utils/helpers/dashboard_home/__init__.py

"""
Dashboard Home Helpers - Arquitetura Modular

Estrutura:
├── header_helper.py     # Cabeçalho (4 campos)
├── mercado_helper.py    # Score Mercado (4 campos)
├── risco_helper.py      # Score Risco (4 campos)
├── aggregator.py        # Orquestrador
└── database_helper.py   # CRUD PostgreSQL

Fluxo:
aggregator → helpers → database → response
"""

from .aggregator import collect_all_dashboard_data
from .database_helper import insert_dashboard_data, get_latest_dashboard
from .header_helper import get_header_data
from .mercado_helper import get_mercado_data
from .risco_helper import get_risco_data