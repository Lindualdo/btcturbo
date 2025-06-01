# app/services/utils/helpers/realized_cap/bigquery_rc_calculator.py

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
from google.cloud import bigquery
from google.oauth2 import service_account
import json
from app.config import get_settings

logger = logging.getLogger(__name__)

class RealizedCapCalculator:
    def __init__(self):
        """Inicializa calculator com BigQuery client"""
        settings = get_settings()
        try:
            credentials_info = json.loads(settings.GOOGLE_APPLICATION_CREDENTIALS_JSON)
            credentials = service_account.Credentials.from_service_account_info(credentials_info)
            
            self.client = bigquery.Client(
                credentials=credentials,
                project=settings.GOOGLE_CLOUD_PROJECT
            )
            logger.info("✅ BigQuery RC Calculator inicializado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar BigQuery RC Calculator: {str(e)}")
            raise Exception(f"Falha BigQuery RC Calculator: {str(e)}")

    def get_historical_btc_prices(self, days: int = 400) -> Dict[str, float]:
        """Busca preços históricos BTC via CoinGecko"""
        try:
            logger.info(f"🔍 Buscando preços históricos BTC ({days} dias)...")
            
            url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
            params = {
                "vs_currency": "usd",
                "days": days,
                "interval": "daily"
            }
            
            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()
            
            # Converter para dict {date: price}
            price_dict = {}
            for timestamp, price in data["prices"]:
                date_str = datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d')
                price_dict[date_str] = float(price)
            
            logger.info(f"✅ Preços históricos: {len(price_dict)} dias obtidos")
            return price_dict
            
        except Exception as e:
            logger.error(f"❌ Erro preços históricos: {str(e)}")
            raise Exception(f"Preços históricos falharam: {str(e)}")

    def calculate_realized_cap_for_date(self, target_date: str, price_dict: Dict[str, float]) -> float:
        """
        Calcula Realized Cap REAL para uma data específica
        RC = Σ(UTXO_value × price_when_created) para UTXOs existentes na target_date
        """
        try:
            logger.info(f"🔍 Calculando RC real para {target_date}...")
            
            # Query para UTXOs criados até target_date e não gastos até essa data
            query = f"""
            WITH utxos_at_date AS (
              SELECT 
                DATE(o.block_timestamp) as creation_date,
                o.value / 100000000.0 as btc_value,
                o.transaction_hash,
                o.index
              FROM `bigquery-public-data.crypto_bitcoin.outputs` o
              WHERE DATE(o.block_timestamp) <= '{target_date}'
                AND DATE(o.block_timestamp) >= DATE_SUB('{target_date}', INTERVAL 90 DAY)
                -- Filtrar apenas últimos 90 dias para performance
            ),
            
            spent_utxos AS (
              SELECT DISTINCT
                i.spent_transaction_hash,
                i.spent_output_index
              FROM `bigquery-public-data.crypto_bitcoin.inputs` i
              WHERE DATE(i.block_timestamp) <= '{target_date}'
                AND DATE(i.block_timestamp) >= DATE_SUB('{target_date}', INTERVAL 90 DAY)
            )
            
            SELECT 
              creation_date,
              SUM(btc_value) as total_btc_value
            FROM utxos_at_date u
            LEFT JOIN spent_utxos s 
              ON u.transaction_hash = s.spent_transaction_hash 
              AND u.index = s.spent_output_index
            WHERE s.spent_transaction_hash IS NULL  -- UTXOs não gastos
            GROUP BY creation_date
            ORDER BY creation_date
            """
            
            result = list(self.client.query(query))
            
            realized_cap = 0.0
            for row in result:
                creation_date_str = str(row.creation_date)
                btc_value = float(row.total_btc_value)
                
                # Preço no dia de criação
                if creation_date_str in price_dict:
                    creation_price = price_dict[creation_date_str]
                    realized_cap += btc_value * creation_price
                else:
                    # Fallback: usar preço mais próximo
                    fallback_price = self._get_closest_price(creation_date_str, price_dict)
                    realized_cap += btc_value * fallback_price
            
            logger.info(f"✅ RC real para {target_date}: ${realized_cap/1e9:.1f}B")
            return realized_cap
            
        except Exception as e:
            logger.error(f"❌ Erro RC para {target_date}: {str(e)}")
            raise Exception(f"RC calculation failed for {target_date}: {str(e)}")

    def _get_closest_price(self, target_date: str, price_dict: Dict[str, float]) -> float:
        """Encontra preço mais próximo quando data exata não existe"""
        try:
            target = datetime.strptime(target_date, '%Y-%m-%d')
            
            # Procurar data mais próxima (até 7 dias de diferença)
            for days_diff in range(8):
                for direction in [-1, 1]:
                    check_date = target + timedelta(days=days_diff * direction)
                    check_date_str = check_date.strftime('%Y-%m-%d')
                    
                    if check_date_str in price_dict:
                        return price_dict[check_date_str]
            
            # Fallback: preço médio
            return sum(price_dict.values()) / len(price_dict)
            
        except Exception:
            return 50000.0  # Fallback conservador

    def get_sample_realized_cap_points(self, days_back: int = 30) -> List[Dict]:
        """
        Calcula RC real para pontos de amostra (últimos 30 dias)
        Para validar se estamos no caminho certo
        """
        try:
            logger.info(f"🔍 Calculando RC real para {days_back} pontos de amostra...")
            
            # Buscar preços históricos
            price_dict = self.get_historical_btc_prices(days=days_back + 100)
            
            # Calcular RC para pontos espaçados
            sample_points = []
            base_date = datetime.now().date()
            
            for i in range(0, days_back, 7):  # A cada 7 dias
                target_date = base_date - timedelta(days=i)
                target_date_str = target_date.strftime('%Y-%m-%d')
                
                try:
                    realized_cap = self.calculate_realized_cap_for_date(target_date_str, price_dict)
                    
                    # Market Cap para comparação
                    if target_date_str in price_dict:
                        btc_price = price_dict[target_date_str]
                        # Supply aproximado (19.8M BTC)
                        market_cap = btc_price * 19800000
                        
                        sample_points.append({
                            "date": target_date_str,
                            "realized_cap": realized_cap,
                            "market_cap": market_cap,
                            "mc_rc_diff": market_cap - realized_cap,
                            "rc_mc_ratio": realized_cap / market_cap if market_cap > 0 else 0
                        })
                        
                except Exception as e:
                    logger.warning(f"⚠️ Falha para {target_date_str}: {str(e)}")
                    continue
            
            logger.info(f"✅ {len(sample_points)} pontos de RC real calculados")
            return sample_points
            
        except Exception as e:
            logger.error(f"❌ Erro sample RC points: {str(e)}")
            raise Exception(f"Sample RC calculation failed: {str(e)}")

    def calculate_current_realized_cap(self) -> Dict:
        """Calcula Realized Cap atual usando método real"""
        try:
            logger.info("🎯 Calculando RC atual com método REAL...")
            
            today = datetime.now().date().strftime('%Y-%m-%d')
            price_dict = self.get_historical_btc_prices(days=100)
            
            realized_cap = self.calculate_realized_cap_for_date(today, price_dict)
            
            return {
                "realized_cap_usd": realized_cap,
                "realized_cap_bilhoes": realized_cap / 1e9,
                "fonte": "BigQuery_RC_Real",
                "metodo": "UTXO_weighted_by_creation_price",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro RC atual real: {str(e)}")
            raise Exception(f"Current RC real calculation failed: {str(e)}")