# app/services/dashboards/dash_finance/queries/capital_investido_query.py

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def get_capital_investido_data(data_inicio) -> list:
    """
    Mock Capital Investido (Posição Total)
    TODO: Implementar query real supplied_asset_value após validação
    """
    try:
        # Calcular dias desde data_inicio
        dias_diff = (datetime.utcnow() - data_inicio).days
        total_dias = min(dias_diff, 365)  # Máximo 1 ano
        
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