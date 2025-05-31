# app/services/utils/helpers/realized_cap_helper.py

import logging
from google.cloud import bigquery
from google.oauth2 import service_account
import requests
from datetime import datetime, timedelta
from typing import Optional, Tuple
import json
from app.config import get_settings

logger = logging.getLogger(__name__)

class BigQueryHelper:
    def __init__(self):
        """Inicializa cliente BigQuery"""
        settings = get_settings()
        try:
            # Parse das credenciais JSON
            credentials_info = json.loads(settings.GOOGLE_APPLICATION_CREDENTIALS_JSON)
            credentials = service_account.Credentials.from_service_account_info(credentials_info)
            
            self.client = bigquery.Client(
                credentials=credentials,
                project=settings.GOOGLE_CLOUD_PROJECT
            )
            logger.info("✅ BigQuery client inicializado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar BigQuery: {str(e)}")
            raise Exception(f"Falha BigQuery: {str(e)}")

    def test_connection(self) -> bool:
        """Testa conexão BigQuery"""
        try:
            query = "SELECT 1 as test"
            result = list(self.client.query(query))
            logger.info("✅ Conexão BigQuery OK")
            return True
        except Exception as e:
            logger.error(f"❌ Teste BigQuery falhou: {str(e)}")
            return False

    def get_realized_cap_simplified(self) -> float:
        """
        Calcula Realized Cap usando aproximação simples
        Usa dados agregados diários ao invés de todos UTXOs individuais
        """
        try:
            logger.info("🔍 Calculando Realized Cap via BigQuery...")
            
            # Query otimizada - usa dados agregados por dia
            query = """
            WITH daily_prices AS (
              SELECT 
                DATE(block_timestamp) as date,
                AVG(outputs.value) as avg_output_value,
                COUNT(*) as output_count,
                -- Aproximação do preço médio do dia (via coinbase ou exchanges)
                APPROX_QUANTILES(
                  SAFE_DIVIDE(
                    (SELECT SUM(output_value) FROM UNNEST(outputs) as output_value), 
                    100000000
                  ), 100
                )[ORDINAL(50)] as approx_btc_price
              FROM `bigquery-public-data.crypto_bitcoin.transactions`
              WHERE DATE(block_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
              GROUP BY DATE(block_timestamp)
            ),
            
            unspent_outputs AS (
              SELECT 
                DATE(block_timestamp) as creation_date,
                SUM(output_value) as total_value_satoshis
              FROM `bigquery-public-data.crypto_bitcoin.outputs`
              WHERE is_spent = FALSE 
                AND DATE(block_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
              GROUP BY DATE(block_timestamp)
            )
            
            SELECT 
              SUM(
                (unspent.total_value_satoshis / 100000000.0) * 
                COALESCE(prices.approx_btc_price, 50000)  -- fallback price
              ) as realized_cap_usd
            FROM unspent_outputs unspent
            LEFT JOIN daily_prices prices ON unspent.creation_date = prices.date
            """
            
            result = list(self.client.query(query))
            
            if result and len(result) > 0:
                realized_cap = float(result[0].realized_cap_usd or 0)
                
                # Validação: Realized Cap deve estar entre $200B-$1T
                if 200e9 <= realized_cap <= 1e12:
                    logger.info(f"✅ Realized Cap BigQuery: ${realized_cap/1e9:.1f}B")
                    return realized_cap
                else:
                    logger.warning(f"⚠️ Realized Cap BigQuery fora do range: ${realized_cap/1e9:.1f}B")
                    return realized_cap
            else:
                raise Exception("Query BigQuery retornou vazia")
                
        except Exception as e:
            logger.error(f"❌ Erro BigQuery Realized Cap: {str(e)}")
            raise Exception(f"BigQuery falhou: {str(e)}")

def get_realized_cap_fallback() -> Tuple[float, str]:
    """
    Fallback para Realized Cap usando APIs públicas
    """
    sources = [
        {
            "name": "CryptoQuant_Free",
            "url": "https://api.cryptoquant.com/v1/btc/network-indicator/realized-cap",
            "parser": lambda r: r.json()["result"]["data"][-1]["value"]
        },
        {
            "name": "Glassnode_Free", 
            "url": "https://api.glassnode.com/v1/metrics/market/marketcap_realized",
            "parser": lambda r: r.json()[-1]["v"]
        }
    ]
    
    for source in sources:
        try:
            logger.info(f"🔍 Buscando Realized Cap via {source['name']}")
            
            headers = {"User-Agent": "BTC-Turbo/1.0"}
            response = requests.get(source["url"], headers=headers, timeout=15)
            
            if response.status_code == 200:
                realized_cap = source["parser"](response)
                realized_cap = float(realized_cap)
                
                # Validação
                if 200e9 <= realized_cap <= 1e12:
                    logger.info(f"✅ Realized Cap {source['name']}: ${realized_cap/1e9:.1f}B")
                    return realized_cap, source['name']
                    
        except Exception as e:
            logger.warning(f"❌ Falha {source['name']}: {str(e)}")
            continue
    
    # Última alternativa: estimativa baseada em heurística
    logger.warning("⚠️ Usando estimativa Realized Cap")
    estimated_rc = 450e9  # ~$450B estimativa conservadora
    return estimated_rc, "estimated"

def get_current_realized_cap() -> dict:
    """
    Calcula Realized Cap atual com fallback
    """
    try:
        logger.info("🎯 Iniciando cálculo Realized Cap...")
        
        # Tentar BigQuery primeiro
        try:
            bigquery_helper = BigQueryHelper()
            
            # Testar conexão
            if bigquery_helper.test_connection():
                realized_cap = bigquery_helper.get_realized_cap_simplified()
                source = "BigQuery"
            else:
                raise Exception("Conexão BigQuery falhou")
                
        except Exception as e:
            logger.warning(f"⚠️ BigQuery falhou, usando fallback: {str(e)}")
            realized_cap, source = get_realized_cap_fallback()
        
        result = {
            "realized_cap_usd": realized_cap,
            "realized_cap_bilhoes": realized_cap / 1e9,
            "fonte": source,
            "validacao": {
                "range_ok": 200e9 <= realized_cap <= 1e12,
                "valor_plausivel": 300e9 <= realized_cap <= 800e9
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"✅ Realized Cap calculado: ${realized_cap/1e9:.1f}B (fonte: {source})")
        return result
        
    except Exception as e:
        logger.error(f"❌ Erro no cálculo Realized Cap: {str(e)}")
        raise Exception(f"Falha no Realized Cap: {str(e)}")

def compare_realized_cap_sources() -> dict:
    """Compara BigQuery vs APIs externas"""
    try:
        results = {}
        
        # BigQuery
        try:
            bigquery_helper = BigQueryHelper()
            bq_rc = bigquery_helper.get_realized_cap_simplified()
            results["bigquery"] = {"value": bq_rc, "status": "success"}
        except Exception as e:
            results["bigquery"] = {"value": None, "status": f"error: {str(e)}"}
        
        # Fallback APIs
        try:
            fallback_rc, fallback_source = get_realized_cap_fallback()
            results["fallback"] = {"value": fallback_rc, "source": fallback_source, "status": "success"}
        except Exception as e:
            results["fallback"] = {"value": None, "status": f"error: {str(e)}"}
        
        # Comparação
        if results["bigquery"]["status"] == "success" and results["fallback"]["status"] == "success":
            bq_val = results["bigquery"]["value"]
            fb_val = results["fallback"]["value"]
            diff_pct = abs(bq_val - fb_val) / fb_val if fb_val > 0 else 0
            
            results["comparison"] = {
                "difference_percent": diff_pct,
                "acceptable": diff_pct < 0.20,  # 20% tolerância
                "status": "✅ CONVERGEM" if diff_pct < 0.20 else "⚠️ DIVERGEM"
            }
        
        return results
        
    except Exception as e:
        return {"error": str(e)}