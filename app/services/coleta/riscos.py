# app/services/coleta/riscos.py

from datetime import datetime
import logging
from app.services.utils.helpers.web3_helper import get_aave_position
from app.services.utils.helpers.tradingview.price_helper import get_btc_price
from app.services.utils.helpers.postgres.indicadores.risco_helper import insert_dados_risco_completo
from app.config import get_settings

logger = logging.getLogger(__name__)

def coletar(forcar_coleta: bool):
    """Coleta dados de risco via AAVE Web3"""
    try:
        settings = get_settings()
        
        logger.info("🔄 Iniciando coleta de dados RISCO via AAVE...")
        
        # 1. Buscar preço BTC atual
        logger.info("📊 Buscando preço BTC...")
        btc_price = get_btc_price()
        
        # 2. Buscar dados AAVE
        logger.info("🔗 Conectando AAVE via Web3...")
        wallet_address = settings.WALLET_ADDRESS  # Adicionar no config.py
        aave_data = get_aave_position(wallet_address, btc_price)
        
        # 3. Gravar no PostgreSQL
        logger.info("💾 Gravando dados no PostgreSQL...")
        success = insert_dados_risco_completo(
            dist_liquidacao=aave_data["dist_liquidacao"],
            health_factor=aave_data["health_factor"],
            btc_price=aave_data["btc_price"],
            total_borrowed=aave_data["total_borrowed"],
            supplied_asset_value=aave_data["supplied_asset_value"],
            net_asset_value=aave_data["net_asset_value"],
            alavancagem=aave_data["alavancagem"],
            fonte="aave/web3",
            liquidation_price=aave_data["liquidation_price"]
        )
        
        if success:
            return {
                "bloco": "riscos",
                "status": "sucesso",
                "timestamp": datetime.utcnow().isoformat(),
                "detalhes": "Dados coletados via AAVE Web3",
                "dados_coletados": {
                    "health_factor": aave_data["health_factor"],
                    "dist_liquidacao": f"{aave_data['dist_liquidacao']:.1f}%",
                    "alavancagem": f"{aave_data['alavancagem']:.2f}x",
                    "btc_price": f"${aave_data['btc_price']:,.2f}",
                    "net_asset_value": f"${aave_data['net_asset_value']:,.2f}"
                },
                "fonte": "aave/web3"
            }
        else:
            raise Exception("Falha ao gravar dados no PostgreSQL")
            
    except Exception as e:
        logger.error(f"❌ Erro na coleta de riscos: {str(e)}")
        return {
            "bloco": "riscos",
            "status": "erro",
            "timestamp": datetime.utcnow().isoformat(),
            "detalhes": f"Falha na coleta: {str(e)}",
            "fonte": "aave/web3"
        }