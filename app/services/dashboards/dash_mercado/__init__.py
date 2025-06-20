# app/services/v3/dash_mercado/__init__.py

"""
Dashboard Mercado Helpers - v1.0

Módulos:
├── data_collector.py      # Coleta dados dos 3 blocos
├── score_calculator.py    # Calcula scores usando funções existentes
├── database_helper.py     # CRUD PostgreSQL
└── main_functions.py      # Funções principais exportadas

Fluxo:
collect_and_calculate_scores() → save_dashboard_scores() → get_latest_dashboard_scores()
"""