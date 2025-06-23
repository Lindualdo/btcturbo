# app/services/utils/helpers/web3_helper.py

from web3 import Web3
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)

class AAVEHelper:
    def __init__(self):
        settings = get_settings()
        self.alchemy_api_key = getattr(settings, 'ALCHEMY_API_KEY', None)
        self.initialize_web3()
        self.pool_address = "0x794a61358D6845594F94dc1DB02A252b5b4814aD"  # AAVE Arbitrum
        
        # AAVE Pool ABI (getUserAccountData function)
        self.pool_abi = [
            {
                "inputs": [{"internalType": "address", "name": "user", "type": "address"}],
                "name": "getUserAccountData",
                "outputs": [
                    {"internalType": "uint256", "name": "totalCollateralBase", "type": "uint256"},
                    {"internalType": "uint256", "name": "totalDebtBase", "type": "uint256"},
                    {"internalType": "uint256", "name": "availableBorrowsBase", "type": "uint256"},
                    {"internalType": "uint256", "name": "currentLiquidationThreshold", "type": "uint256"},
                    {"internalType": "uint256", "name": "ltv", "type": "uint256"},
                    {"internalType": "uint256", "name": "healthFactor", "type": "uint256"}
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        self.pool_contract = self.w3.eth.contract(
            address=self.pool_address,
            abi=self.pool_abi
        )

    def initialize_web3(self):
        """Inicializa a conexão Web3 com Alchemy"""
        try:
            if self.alchemy_api_key:
                alchemy_url = f"https://eth-mainnet.g.alchemy.com/v2/{self.alchemy_api_key}"
                self.w3 = Web3(Web3.HTTPProvider(alchemy_url))
                logger.info(f"Web3 conectado: {self.w3.is_connected()}")
            else:
                logger.warning("Alchemy API Key não configurada")
                # Tentar RPC público como fallback
                public_rpc = "https://arb1.arbitrum.io/rpc"
                self.w3 = Web3(Web3.HTTPProvider(public_rpc))
                logger.info(f"Web3 conectado a RPC público: {self.w3.is_connected()}")
        except Exception as e:
            logger.error(f"Erro ao inicializar Web3: {str(e)}")
            raise

    def get_user_account_data(self, wallet_address: str) -> dict:
        """Busca dados da conta no AAVE"""
        try:
            logger.info(f"🔍 Buscando dados AAVE para {wallet_address}")
            
            # Converter endereço para checksum
            wallet = Web3.to_checksum_address(wallet_address)
            
            # Chamar getUserAccountData
            result = self.pool_contract.functions.getUserAccountData(wallet).call()
            
            # Converter valores (AAVE retorna em 8 decimais para valores base)
            data = {
                "total_collateral_base": result[0] / 1e8,  # USD
                "total_debt_base": result[1] / 1e8,       # USD
                "available_borrows_base": result[2] / 1e8, # USD
                "current_liquidation_threshold": result[3] / 1e4,  # % (ex: 8250 = 82.5%)
                "ltv": result[4] / 1e4,                   # % (ex: 7800 = 78%)
                "health_factor": min(result[5] / 1e18, 999999) if result[5] > 0 else 999999
            }
            
            logger.info(f"✅ Dados AAVE obtidos: HF={data['health_factor']:.2f}")
            return data
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar dados AAVE: {str(e)}")
            raise Exception(f"Falha na consulta AAVE: {str(e)}")

    def calculate_metrics(self, aave_data: dict, btc_price: float) -> dict:
        """Calcula métricas derivadas"""
        try:
            total_collateral = aave_data["total_collateral_base"]
            total_debt = aave_data["total_debt_base"]
            health_factor = aave_data["health_factor"]
            
            # Net Asset Value (Collateral - Debt)
            net_asset_value = total_collateral - total_debt
            
            # Alavancagem (Total Collateral / Net Asset Value)
            alavancagem = total_collateral / net_asset_value if net_asset_value > 0 else 0
            
            # Distância para liquidação
            if health_factor <= 1.0:
                dist_liquidacao = 0.0
            else:
                liquidation_price = btc_price / health_factor
                dist_liquidacao = ((btc_price - liquidation_price) / btc_price) * 100
            
            return {
                "supplied_asset_value": total_collateral,
                "total_borrowed": total_debt,
                "net_asset_value": net_asset_value,
                "alavancagem": alavancagem,
                "dist_liquidacao": max(0, dist_liquidacao),
                "health_factor": health_factor,
                "btc_price": btc_price,
                "liquidation_price": liquidation_price,
            }
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo de métricas: {str(e)}")
            raise Exception(f"Falha no cálculo: {str(e)}")

def get_aave_position(wallet_address: str, btc_price: float) -> dict:
    """Função principal para obter posição AAVE completa"""
    aave = AAVEHelper()
    raw_data = aave.get_user_account_data(wallet_address)
    metrics = aave.calculate_metrics(raw_data, btc_price)
    return metrics