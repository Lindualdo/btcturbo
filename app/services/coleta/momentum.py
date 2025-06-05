# app/services/coleta/momentum.py

from datetime import datetime
import logging
from app.services.utils.helpers.notion_helper import get_momentum_data_from_notion
from app.services.utils.helpers.postgres.momentum_helper import insert_dados_momentum

logger = logging.getLogger(__name__)

def coletar(forcar_coleta: bool):
    """
    Coleta dados do bloco MOMENTUM via Notion Database e grava no PostgreSQL
    
    Args:
        forcar_coleta (bool): Se True, força nova coleta independente do cache
        
    Returns:
        dict: Status da coleta com detalhes dos dados coletados
    """
    try:
        logger.info("🔄 Iniciando coleta bloco MOMENTUM via Notion...")
        
        # 1. Buscar dados do Notion
        logger.info("📋 Conectando ao Notion Database...")
        dados_notion = get_momentum_data_from_notion()
        
        if not dados_notion:
            raise Exception("Nenhum dado retornado do Notion Database")
        
        # 2. Extrair indicadores necessários do bloco momentum
        rsi_semanal = dados_notion.get("rsi_semanal")
        funding_rates = dados_notion.get("funding_rates") 
        exchange_netflow = dados_notion.get("exchange_netflow")
        long_short_ratio = dados_notion.get("long_short_ratio")
        
        # 3. Validar se todos os indicadores foram coletados
        indicadores_faltando = []
        if rsi_semanal is None:
            indicadores_faltando.append("rsi_semanal")
        if funding_rates is None:
            indicadores_faltando.append("funding_rates")
        if exchange_netflow is None:
            indicadores_faltando.append("exchange_netflow")
        if long_short_ratio is None:
            indicadores_faltando.append("long_short_ratio")
            
        if indicadores_faltando:
            logger.warning(f"⚠️ Indicadores não encontrados no Notion: {indicadores_faltando}")
            # Continua com os dados disponíveis, usando 0.0 para os faltantes
            rsi_semanal = rsi_semanal or 0.0
            funding_rates = funding_rates or 0.0
            exchange_netflow = exchange_netflow or 0.0
            long_short_ratio = long_short_ratio or 0.0
        
        # 4. Gravar dados no PostgreSQL
        logger.info("💾 Gravando dados no PostgreSQL...")
        sucesso_gravacao = insert_dados_momentum(
            rsi=float(rsi_semanal),
            funding=float(funding_rates),
            netflow=float(exchange_netflow),
            ls_ratio=float(long_short_ratio),
            fonte="notion"
        )
        
        if not sucesso_gravacao:
            raise Exception("Falha ao gravar dados no PostgreSQL")
        
        # 5. Preparar resposta de sucesso
        resposta_sucesso = {
            "bloco": "momentum",
            "status": "sucesso",
            "timestamp": datetime.utcnow().isoformat(),
            "detalhes": "Dados coletados via Notion Database",
            "dados_coletados": {
                "rsi_semanal": float(rsi_semanal),
                "funding_rates": float(funding_rates),
                "exchange_netflow": float(exchange_netflow),
                "long_short_ratio": float(long_short_ratio),
                "fonte_original": dados_notion.get("fonte", "Notion"),
                "timestamp_notion": dados_notion.get("timestamp")
            },
            "fonte": "notion",
            "indicadores_processados": 4,
            "indicadores_faltando": indicadores_faltando if indicadores_faltando else "nenhum"
        }
        
        logger.info(f"✅ Coleta MOMENTUM concluída - RSI: {rsi_semanal}, Funding: {funding_rates}, Netflow: {exchange_netflow}, L/S: {long_short_ratio}")
        return resposta_sucesso
        
    except Exception as e:
        logger.error(f"❌ Erro na coleta MOMENTUM via Notion: {str(e)}")
        
        resposta_erro = {
            "bloco": "momentum", 
            "status": "erro",
            "timestamp": datetime.utcnow().isoformat(),
            "detalhes": f"Falha na coleta via Notion: {str(e)}",
            "fonte": "notion",
            "dados_coletados": None
        }
        
        return resposta_erro