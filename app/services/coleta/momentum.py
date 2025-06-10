# app/services/coleta/momentum.py - SIMPLES

from datetime import datetime
import logging
from app.services.utils.helpers.notion_helper import get_momentum_data_from_notion
from app.services.utils.helpers.postgres.momentum_helper import insert_dados_momentum

logger = logging.getLogger(__name__)

def coletar(forcar_coleta: bool):
    """Coleta dados do bloco MOMENTUM via Notion Database"""
    try:
        logger.info("🔄 Iniciando coleta bloco MOMENTUM...")
        
        # 1. Buscar dados do Notion
        dados_notion = get_momentum_data_from_notion()
        if not dados_notion:
            raise Exception("Nenhum dado retornado do Notion Database")
        
        # 2. Extrair indicadores (igual aos outros)
        rsi_semanal = dados_notion.get("rsi_semanal") or 0.0
        funding_rates = dados_notion.get("funding_rates") or 0.0
        exchange_netflow = dados_notion.get("exchange_netflow") or 0.0
        long_short_ratio = dados_notion.get("long_short_ratio") or 0.0
        sopr = dados_notion.get("sopr") or 0.0
        
        # 3. Gravar no PostgreSQL
        sucesso = insert_dados_momentum(
            rsi=float(rsi_semanal),
            funding=float(funding_rates),
            netflow=float(exchange_netflow),
            ls_ratio=float(long_short_ratio),
            sopr=float(sopr),
            fonte="notion"
        )
        
        if not sucesso:
            raise Exception("Falha ao gravar dados no PostgreSQL")
        
        # 4. Resposta de sucesso
        return {
            "bloco": "momentum",
            "status": "sucesso",
            "timestamp": datetime.utcnow().isoformat(),
            "dados_coletados": {
                "rsi_semanal": float(rsi_semanal),
                "funding_rates": float(funding_rates),
                "exchange_netflow": float(exchange_netflow),
                "long_short_ratio": float(long_short_ratio),
                "sopr": float(sopr),
                "fonte": "notion"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na coleta MOMENTUM: {str(e)}")
        return {
            "bloco": "momentum",
            "status": "erro",
            "timestamp": datetime.utcnow().isoformat(),
            "detalhes": f"Falha na coleta: {str(e)}",
            "fonte": "notion"
        }