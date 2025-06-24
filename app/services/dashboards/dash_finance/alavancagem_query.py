# app/services/dashboards/dash_finance/queries/alavancagem_query.py

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def get_alavancagem_data(data_inicio) -> list:
    """
    Mock Alavancagem Atual vs Permitida
    TODO: Implementar query real após migração dash_main
    """
    try:
        # Calcular dias desde data_inicio
        dias_diff = (datetime.utcnow() - data_inicio).days
        total_dias = min(dias_diff, 365)  # Máximo 1 ano
        
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