# app/services/dashboards/dash_finance/queries_helper.py

import logging
from datetime import datetime, timedelta
from app.services.utils.helpers.postgres.base import execute_query

logger = logging.getLogger(__name__)

def get_health_factor_history(periodo: str) -> list:
    """
    Consulta histórico Health Factor (REAL)
    Último registro de cada dia
    """
    try:
        data_inicio = convert_periodo_to_date(periodo)
        
        query = """
            SELECT 
                DATE(timestamp) as data,
                timestamp,
                health_factor as valor
            FROM indicadores_risco r1
            WHERE timestamp >= %s
              AND health_factor IS NOT NULL
              AND timestamp = (
                SELECT MAX(timestamp) 
                FROM indicadores_risco r2 
                WHERE DATE(r1.timestamp) = DATE(r2.timestamp)
                  AND health_factor IS NOT NULL
              )
            ORDER BY timestamp DESC;
        """
        
        resultados = execute_query(query, params=(data_inicio,), fetch_all=True)
        
        if resultados:
            dados = [
                {
                    "timestamp": row["timestamp"].isoformat(),
                    "valor": float(row["valor"]) if row["valor"] else 0.0
                }
                for row in resultados
            ]
            logger.info(f"✅ Health Factor: {len(dados)} registros obtidos")
            return dados
        else:
            logger.warning("⚠️ Nenhum registro Health Factor encontrado")
            return []
            
    except Exception as e:
        logger.error(f"❌ Erro query Health Factor: {str(e)}")
        return []

def get_alavancagem_history_mock(periodo: str) -> list:
    """Mock para histórico alavancagem"""
    try:
        total_dias = _get_dias_periodo(periodo)
        dados = []
        
        for i in range(total_dias):
            data = datetime.utcnow() - timedelta(days=i)
            dados.append({
                "timestamp": data.isoformat(),
                "atual": round(1.2 + (i * 0.02), 2),
                "permitida": 2.5 if i < 15 else 2.0
            })
        
        logger.info(f"🔧 Alavancagem mock: {len(dados)} registros gerados")
        return dados
        
    except Exception as e:
        logger.error(f"❌ Erro mock Alavancagem: {str(e)}")
        return []

def get_patrimonio_history(periodo: str) -> list:
    """
    Consulta histórico Patrimônio Líquido (REAL)
    Último registro de cada dia
    """
    try:
        data_inicio = convert_periodo_to_date(periodo)
        
        query = """
            SELECT 
                DATE(timestamp) as data,
                timestamp,
                net_asset_value as valor
            FROM indicadores_risco r1
            WHERE timestamp >= %s
              AND net_asset_value IS NOT NULL
              AND timestamp = (
                SELECT MAX(timestamp) 
                FROM indicadores_risco r2 
                WHERE DATE(r1.timestamp) = DATE(r2.timestamp)
                  AND net_asset_value IS NOT NULL
              )
            ORDER BY timestamp DESC;
        """
        
        resultados = execute_query(query, params=(data_inicio,), fetch_all=True)
        
        if resultados:
            dados = [
                {
                    "timestamp": row["timestamp"].isoformat(),
                    "valor": float(row["valor"]) if row["valor"] else 0.0
                }
                for row in resultados
            ]
            logger.info(f"✅ Patrimônio: {len(dados)} registros obtidos")
            return dados
        else:
            logger.warning("⚠️ Nenhum registro Patrimônio encontrado")
            return []
            
    except Exception as e:
        logger.error(f"❌ Erro query Patrimônio: {str(e)}")
        return []

def get_capital_history_mock(periodo: str) -> list:
    """Mock para histórico capital investido"""
    try:
        total_dias = _get_dias_periodo(periodo)
        dados = []
        valor_inicial = 95000.0
        
        for i in range(total_dias):
            data = datetime.utcnow() - timedelta(days=i)
            # Simulação posição total com alavancagem
            variacao = (total_dias - i) * 200 + (i % 7) * 800
            valor = valor_inicial + variacao
            
            dados.append({
                "timestamp": data.isoformat(),
                "valor": round(valor, 2)
            })
        
        logger.info(f"🔧 Capital Investido mock: {len(dados)} registros gerados")
        return dados
        
    except Exception as e:
        logger.error(f"❌ Erro mock Capital Investido: {str(e)}")
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

def _get_dias_periodo(periodo: str) -> int:
    """Retorna número de dias para mocks"""
    if periodo == "30d":
        return 30
    elif periodo == "3m":
        return 90
    elif periodo == "6m":
        return 180
    elif periodo == "1y":
        return 365
    elif periodo == "all":
        return 365  # Máximo para mock
    else:
        return 30