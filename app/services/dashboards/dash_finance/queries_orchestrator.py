# app/services/dashboards/dash_finance/queries_orchestrator.py

import logging
from datetime import datetime, timedelta
from .querys.health_factor_query import get_health_factor_data
from .querys.patrimonio_query import get_patrimonio_data
from .querys.alavancagem_query import get_alavancagem_data
from .querys.capital_investido_query import get_capital_investido_data

logger = logging.getLogger(__name__)

def get_health_factor_history(periodo: str) -> list:
    """Orquestra consulta Health Factor"""
    try:
        data_inicio = convert_periodo_to_date(periodo)
        return get_health_factor_data(data_inicio)
    except Exception as e:
        logger.error(f"❌ Erro orquestrador Health Factor: {str(e)}")
        return []

def get_patrimonio_history(periodo: str) -> list:
    """Orquestra consulta Patrimônio"""
    try:
        data_inicio = convert_periodo_to_date(periodo)
        return get_patrimonio_data(data_inicio)
    except Exception as e:
        logger.error(f"❌ Erro orquestrador Patrimônio: {str(e)}")
        return []

def get_alavancagem_history(periodo: str) -> list:
    """Orquestra consulta Alavancagem"""
    try:
        data_inicio = convert_periodo_to_date(periodo)
        return get_alavancagem_data(data_inicio)
    except Exception as e:
        logger.error(f"❌ Erro orquestrador Alavancagem: {str(e)}")
        return []

def get_capital_history(periodo: str) -> list:
    """Orquestra consulta Capital Investido"""
    try:
        data_inicio = convert_periodo_to_date(periodo)
        return get_capital_investido_data(data_inicio)
    except Exception as e:
        logger.error(f"❌ Erro orquestrador Capital Investido: {str(e)}")
        return []

def convert_periodo_to_date(periodo: str) -> datetime:
    """Converte período string para data inicial"""
    hoje = datetime.utcnow()
    
    if periodo == "30d":
        return hoje - timedelta(days=30)
    elif periodo == "3m":
        return hoje - timedelta(days=90)
    elif periodo == "6m":
        return hoje - timedelta(days=180)
    elif periodo == "1y":
        return hoje - timedelta(days=365)
    elif periodo == "all":
        return datetime(2020, 1, 1)  # Data bem antiga
    else:
        return hoje - timedelta(days=30)  # Default